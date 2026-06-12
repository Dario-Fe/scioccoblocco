#!/usr/bin/env python3
import os
import re
import shutil
import html
import yaml
from pathlib import Path
from markdown import markdown
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent
RECENSIONI_DIR = BASE_DIR / "trekking_recensioni"
OUTPUT_DIR = BASE_DIR / "dist"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
CONTENT_DIR = BASE_DIR / "content"

BASE_PATH = ""

env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
env.globals["base_path"] = BASE_PATH

DIFFICOLTA_MAP = {
    "T": "Turistica",
    "E": "Escursionistica",
    "EE": "Escursionismo Esperto",
    "T/E": "Turistica / Escursionistica",
    "E/EE": "Escursionistica / Esperto",
    "M/F": "Media / Facile",
}

def slugify(text):
    s = text.lower()
    s = re.sub(r'[àáâãäå]', 'a', s)
    s = re.sub(r'[èéêë]', 'e', s)
    s = re.sub(r'[ìíîï]', 'i', s)
    s = re.sub(r'[òóôõö]', 'o', s)
    s = re.sub(r'[ùúûü]', 'u', s)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = s.strip('-')
    return s or "recensione"

INFO_LABELS = [
    'periodo consigliato', 'consigliato',
    'attrezzatura',
    'tempo di percorrenza',
    'dislivello',
    'strutture',
    'come raggiungere',
]

INFO_LABEL_DISPLAY = {
    'periodo consigliato': 'Periodo consigliato',
    'consigliato': 'Periodo consigliato',
    'attrezzatura': 'Attrezzatura',
    'tempo di percorrenza': 'Tempo di percorrenza',
    'dislivello': 'Dislivello',
    'strutture': 'Strutture',
    'come raggiungere': 'Come raggiungere',
}

def parse_field(md_text, label):
    """Parse a single field value for a given label. Returns (value, end_pos) or ('', 0)."""
    parts = label.split()
    if label == 'consigliato':
        lpat = r'(?<!Periodo\s)consigliato'
    else:
        lpat = r'\b' + r'\s+'.join(re.escape(p) for p in parts)

    # Try bold first, then plain text
    for variant in [r'\*\*' + lpat + r'\*\*', lpat]:
        pattern = re.compile(
            variant + r'(?:\s*:)?\s*(.*?)(?=\n\n|\Z|(?=\n(?:\*\*(?:' + all_labels_alt + r')\*\*|(?:' + all_labels_alt + r'))))',
            re.DOTALL | re.IGNORECASE
        )
        m = pattern.search(md_text)
        if m:
            return m.group(1).strip(), m.end()
    return '', 0

def build_all_labels_alt():
    pats = []
    for lb in INFO_LABELS:
        if lb == 'consigliato':
            pats.append(r'(?<!Periodo\s)consigliato')
        else:
            p = lb.split()
            pats.append(r'\b' + r'\s+'.join(re.escape(x) for x in p))
    return '|'.join(pats)

all_labels_alt = build_all_labels_alt()

def parse_info_pairs(md_text):
    pairs = {}
    last_end = 0

    # First pass: bold labels only (more reliable)
    bold_pattern = re.compile(
        r'\*\*([^*]+)\*\*\s*:\s*(.*?)(?=\n\*\*|\n#|\n\n|\Z)', re.DOTALL
    )
    for m in bold_pattern.finditer(md_text):
        k = m.group(1).strip().lower()
        if k not in pairs:
            pairs[k] = m.group(2).strip()
            if m.end() > last_end:
                last_end = m.end()

    # Second pass: all known labels (bold or plain), skip already found
    for label in INFO_LABELS:
        if label in pairs:
            continue
        val, end = parse_field(md_text, label)
        if val:
            pairs[label] = val
            if end > last_end:
                last_end = end

    # For 'come raggiungere': extend value past \n\n
    for key in ('come raggiungere',):
        if key not in pairs:
            continue
        parts = key.split()
        lpat = r'\b' + r'\s+'.join(re.escape(p) for p in parts)
        pattern = re.compile(
            r'(?:\*\*' + lpat + r'\*\*|' + lpat + r')'
            r'(?:\s*:)?\s*',
            re.DOTALL | re.IGNORECASE
        )
        m = pattern.search(md_text)
        if m:
            start = m.end()
            rest = md_text[start:]
            # Find transition from directions to narrative.
            # Step 1: narrative markers — only accept if found within 2 \\n\\n
            # boundaries (otherwise they're deep in narrative, not a transition).
            cut = None
            nm = re.search(
                r'\n\n(?:'
                r'Il sentiero|Il percorso|Il cammino|La traccia'
                r'|Si parte|Partiamo|Inizia|Partendo'
                r'|Lasciata\s+(?:l\'auto|la\s+macchina)|Lasciamo\s+l\'auto'
                r'|Giunti\s+a|Arrivati\s+(?:in|a)'
                r'|Qui\s+a(?!l\s)'  # 'Qui a' but not 'Qui al [word]' (direction)
                r'|Proseguiamo|Dopo\s+aver\s+parcheggiato'
                r')',
                rest[:1500], re.IGNORECASE
            )
            if nm:
                n_nn = rest.count('\n\n', 0, nm.start())
                if n_nn <= 2:
                    cut = nm
            # Step 2: fallback — altitude (xxxm) within first 1000 chars.
            if not cut:
                am = re.search(r'\(\d+\s*m\)', rest[:1000])
                if am:
                    cut_at = rest.rfind('\n\n', 0, am.start())
                    if cut_at >= 0:
                        class _C: start = lambda self: cut_at
                        cut = _C()
            # Step 3: fallback — image ![ within first 1000 chars.
            if not cut:
                im = re.search(r'!\[', rest[:1000])
                if im:
                    cut_at = rest.rfind('\n\n', 0, im.start())
                    if cut_at >= 0:
                        class _CC: start = lambda self: cut_at
                        cut = _CC()
            if cut:
                extended = rest[:cut.start()].strip()
                pairs[key] = extended
                new_end = start + cut.start()
                if new_end > last_end:
                    last_end = new_end
            # else: keep original value

    return pairs, last_end

def extract_title(md_text):
    match = re.match(r'^#\s+(.+)$', md_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Recensione"

def extract_excerpt(md_text):
    fm_match = re.match(r'^---\n.*?\n---\n*', md_text, re.DOTALL)
    body = md_text[fm_match.end():] if fm_match else md_text
    body = re.sub(r'!\[.*?\]\(.*?\)', '', body)

    combined = ''
    for line in body.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            if combined:
                break
            continue
        if combined and combined[-1].isalpha() and line[0].isalpha():
            combined += ' '
        combined += line
        if len(combined) > 200:
            break

    combined = re.sub(r'\*\*(.*?)\*\*', r'\1', combined)
    combined = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', combined)

    if len(combined) > 200:
        combined = combined[:combined.rfind(' ', 0, 200)] + '...'
    return combined.strip()

# Map frontmatter underscore keys to build.py space-separated label keys
FM_TO_LABEL = {
    'periodo_consigliato': 'periodo consigliato',
    'attrezzatura': 'attrezzatura',
    'tempo_di_percorrenza': 'tempo di percorrenza',
    'dislivello': 'dislivello',
    'strutture': 'strutture',
    'come_raggiungere': 'come raggiungere',
}

def parse_frontmatter(md_text):
    """Extract YAML frontmatter (between --- markers). Returns (pairs, body_without_fm).
    Falls back to inline parsing if no frontmatter found."""
    m = re.match(r'^---\n(.*?)\n---\n*', md_text, re.DOTALL)
    if not m:
        return None, md_text
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None, md_text
    if not isinstance(fm, dict):
        return None, md_text

    pairs = {}
    body = md_text[m.end():]
    for fm_key, label_key in FM_TO_LABEL.items():
        val = fm.get(fm_key)
        if val and isinstance(val, str):
            val = val.strip()
            # Collapse newlines to spaces (YAML literal block scalars preserve them)
            val = re.sub(r'\s+', ' ', val)
            pairs[label_key] = val
    return pairs, body


def convert_markdown_to_html(md_text):
    # Try frontmatter first, fall back to inline parsing
    fm_pairs, body_clean = parse_frontmatter(md_text)
    if fm_pairs is not None:
        info = fm_pairs
        body = body_clean
        body = re.sub(r'^#\s+.*$', '', body, flags=re.MULTILINE).lstrip()
        body = re.sub(r'^\n+', '', body).strip()
    else:
        body = re.sub(r'^#\s+.*$', '', md_text, flags=re.MULTILINE).lstrip()
        info, meta_end = parse_info_pairs(md_text)
        if meta_end:
            body_start_in_md = md_text.index(body)
            rel_end = meta_end - body_start_in_md
            if 0 < rel_end < len(body):
                body = body[rel_end:]
        body = re.sub(r'^\n+', '', body).strip()
    title = extract_title(md_text)
    excerpt = extract_excerpt(md_text)
    body_html = markdown(body, extensions=['md_in_html', 'fenced_code'])
    return title, info, excerpt, body_html

def discover_reviews():
    """Scan filesystem for .md files and extract metadata from YAML frontmatter."""
    records = []
    pattern = re.compile(r'^(\d+)_(.+)\.md$')

    for md_file in sorted(RECENSIONI_DIR.glob('*.md')):
        m = pattern.match(md_file.name)
        if not m:
            print(f"  SKIP {md_file.name}: filename doesn't match pattern")
            continue
        num = int(m.group(1))
        name_stub = m.group(2)

        text = md_file.read_text(encoding='utf-8')
        fm_match = re.match(r'^---\n(.*?)\n---\n*', text, re.DOTALL)
        if not fm_match:
            print(f"  SKIP {md_file.name}: no frontmatter found")
            continue

        try:
            fm = yaml.safe_load(fm_match.group(1))
        except yaml.YAMLError:
            print(f"  SKIP {md_file.name}: invalid YAML frontmatter")
            continue

        if not isinstance(fm, dict):
            print(f"  SKIP {md_file.name}: frontmatter not a dict")
            continue

        images_dir = f"images_{num:02d}"
        if not (RECENSIONI_DIR / images_dir).exists():
            images_dir = f"images_{num}"

        name = fm.get('title', '').strip() or name_stub.replace('_', ' ')
        valle = str(fm.get('valle', '')).strip()
        data = str(fm.get('data', '')).strip()
        difficolta = str(fm.get('difficolta', '')).strip()

        records.append({
            "num": num,
            "valle": valle,
            "name": name,
            "data": data,
            "difficolta": difficolta,
            "markdown": md_file.name,
            "images": images_dir,
        })

    return records

def build():
    if OUTPUT_DIR.exists():
        try:
            shutil.rmtree(OUTPUT_DIR)
        except PermissionError:
            pass
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    static_out = OUTPUT_DIR / "static"
    shutil.copytree(STATIC_DIR, static_out)

    records = discover_reviews()
    reviews = []
    valli_set = set()

    recensioni_dir = OUTPUT_DIR / "recensioni"
    recensioni_dir.mkdir(parents=True)

    for rec in records:
        md_file = RECENSIONI_DIR / rec["markdown"]
        img_dir_src = RECENSIONI_DIR / rec["images"]

        if not md_file.exists():
            print(f"  SKIP: {rec['markdown']} non trovato")
            continue

        with open(md_file, 'r', encoding='utf-8') as f:
            md_text = f.read()

        img_prefix = rec["images"]
        md_text = re.sub(r'!\[' + img_prefix + r'/', '![', md_text)
        md_text = md_text.replace('](' + img_prefix + '/', '](images/')

        title, info, excerpt, body_html = convert_markdown_to_html(md_text)

        slug = slugify(rec["name"])

        diff_class = rec["difficolta"].lower().replace('/', '-').replace(' ', '')

        review = {
            "num": rec["num"],
            "valle": rec["valle"],
            "name": rec["name"] or title,
            "data": rec["data"],
            "difficolta": rec["difficolta"],
            "difficolta_class": diff_class,
            "excerpt": excerpt,
            "slug": slug,
        }
        reviews.append(review)
        valli_set.add(rec["valle"])

        review_dir = recensioni_dir / slug
        review_dir.mkdir(parents=True, exist_ok=True)

        if img_dir_src.exists():
            review_img_dir = review_dir / "images"
            if review_img_dir.exists():
                shutil.rmtree(review_img_dir)
            shutil.copytree(img_dir_src, review_img_dir)

        html_content = body_html

        tpl = env.get_template("recensione.html")
        page_html = tpl.render(
            current="recensioni",
            review=review,
            info=info,
            content_html=html_content,
        )
        with open(review_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(page_html)

        print(f"  OK: {rec['num']:02d} - {rec['name']} ({slug})")

    reviews.sort(key=lambda r: r["num"])
    reviews.reverse()

    valli = sorted(valli_set)

    tpl = env.get_template("index.html")
    index_html = tpl.render(current="home", reviews=reviews, valli=valli)
    with open(OUTPUT_DIR / "index.html", 'w', encoding='utf-8') as f:
        f.write(index_html)

    tpl_recensioni = env.get_template("index.html")
    recensioni_html = tpl_recensioni.render(current="recensioni", reviews=reviews, valli=valli)
    recensioni_index = recensioni_dir / "index.html"
    with open(recensioni_index, 'w', encoding='utf-8') as f:
        f.write(recensioni_html)

    for page in ["chi-siamo", "contatti"]:
        md_page = CONTENT_DIR / f"{page}.md"
        page_dir = OUTPUT_DIR / page
        page_dir.mkdir(exist_ok=True)
        content_html = ""
        if md_page.exists():
            with open(md_page, 'r', encoding='utf-8') as f:
                content_html = markdown(f.read(), extensions=['md_in_html'])

        tpl = env.get_template(f"{page}.html")
        page_html = tpl.render(current=page, content_html=content_html)
        with open(page_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(page_html)
        print(f"  OK: {page}/")

    print(f"\nSito generato in: {OUTPUT_DIR}")
    print(f"Recensioni: {len(reviews)}")
    print(f"Valli: {len(valli)}")

if __name__ == "__main__":
    print("Build ScioccoBlocco Site...\n")
    build()
