# AGENTS.md — ScioccoBlocco Trekking Reviews

## Stato attuale

85 recensioni trekking da `scioccoblocco.com/recensioni/`, convertite in markdown auto-contenuto con immagini. Sito statico generato con Python + Jinja2 + Markdown.

## Struttura progetto (FINALE/)

```
FINALE/
├── build.py                  # Build script principale
├── requirements.txt          # Dipendenze Python
├── netlify.toml              # Config deploy Netlify
├── .gitignore                # Ignora dist/ e __pycache__/
├── AGENTS.md                 # Questo file
├── content/
│   ├── chi-siamo.md
│   └── contatti.md
├── static/
│   ├── style.css             # CSS responsive
│   ├── sciocco_logo_new_trasp_piccolo.png   # Logo (leggero)
│   ├── sciocco_logo_new_trasp.png           # Logo (full size)
│   ├── hero_pic.jpg          # Hero background
│   ├── 1bg_top_03.gif        # Logo storico (backup)
│   └── ... (icone, banner)
├── templates/
│   ├── base.html             # Template base (header + nav + footer)
│   ├── index.html            # Home con griglia + filtri
│   ├── recensione.html       # Pagina singola recensione
│   ├── chi-siamo.html
│   └── contatti.html
└── trekking_recensioni/
    ├── NN_Nome_Recensione.md  # 85 file auto-contenuti
    ├── images_NN/             # 85 cartelle immagini (778 foto totali)
    └── _index.csv             # Indice storico (non serve al build)
```

## Build

```bash
pip install -r requirements.txt
python build.py
# Output: dist/
```

## Deploy (Netlify)

1. Push `FINALE/` su GitHub
2. Collega repo a Netlify:
   - Build command: `pip install -r requirements.txt && python build.py`
   - Publish directory: `dist/`

## Formato file .md

Ogni file ha frontmatter YAML + corpo markdown. Le immagini referenziate con `![](images_NN/nome.jpg)`.

```yaml
---
title: "Titolo"
valle: Valle Ossola
data: "agosto 2003"
difficolta: E
periodo_consigliato: Da aprile a ottobre
attrezzatura: Comode scarpe da montagna
tempo_di_percorrenza: 4.30h
dislivello: Totale 500m
strutture: Rifugio XYZ
come_raggiungere: |
  Paragrafo 1...
  Paragrafo 2...
---
```

## Storia modifiche

### Giugno 2026

- **Auto-contenimento**: ogni `.md` ha tutto (frontmatter YAML, immagini). Nessuna dipendenza da `_index.csv`
- **Bold restoration**: `restore_bolds.py` recupera 1955 grassetti (`**bold**`) dagli `<strong>` dell'HTML originale
- **Header redesign**: bianco, logo (`55px`) + nav inline, invece del blu pieno
- **Nuovo logo**: `sciocco_logo_new_trasp_piccolo.png` (trasparente, leggero)
- **FINALE/**: cartella pulita con soli file essenziali per GitHub/Netlify

### Script ausiliari (non in FINALE/)

Nella directory root `D:\Nuovo ScioccoBlocco\ScioccoBlocco\`:

| Script | Scopo |
|--------|-------|
| `restore_bolds.py` | Recupera **grassetto** dall'HTML originale (85 file, 1955 match) |
| `cleanup_asterisks.py` | Pulisce `****` doppi |
| `fix_double_bolds.py` | Normalizza residui `****` → `**` |

### Build details

- `build.py` usa `discover_reviews()` per scansione filesystem (pattern `NN_*.md`)
- Immagini derivate dal numero `NN` → `images_NN/`
- `parse_frontmatter()` per YAML; fallback a parsing inline
- Parsing multi-paragrafo per `come_raggiungere` con narrative markers
- Filtri JS per valle, difficoltà, ricerca testo
- Ordine: dalla più recente alla più vecchia
