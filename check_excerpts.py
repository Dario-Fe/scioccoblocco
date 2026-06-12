import sys; sys.path.insert(0, '.')
from build import extract_excerpt
from pathlib import Path
rec_dir = Path('trekking_recensioni')
short = [(f.name, extract_excerpt(f.read_text(encoding='utf-8'))) for f in sorted(rec_dir.glob('*.md'))]
for n, e in short:
    if len(e.split()) <= 3:
        print(f'{n}: "{e}"')
print(f'\nTotal with <=3 words: {sum(1 for _,e in short if len(e.split())<=3)}')
