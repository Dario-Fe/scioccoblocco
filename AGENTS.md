# AGENTS.md — Progetto Recensioni Trekking (ScioccoBlocco)

## Stato attuale

85 recensioni Trekking estratte da `https://www.scioccoblocco.com/recensioni/rece.php`, convertite in markdown con immagini.

## Struttura output

```
C:\Users\Archivio\Desktop\test\trekking_recensioni\
  01_Cicogna-Alpe_Pre-Pogallo-Cicogna.md      (7.8 KB)
  02_Archia-Monte_Zeda-Sentiero_Cadorna.md    (7.5 KB)
  03_...md
  ...
  85_Rifugio_Gattascosa_(CIASPOLE).md         (7.9 KB)
  _index.csv                                   (CSV indice)
  images_01/                                   (5 immagini)
  images_02/                                   (2 immagini)
  ...
  images_85/                                   (8 immagini)
```

- **85 file .md** numerati `NN_Nome_Recensione.md` (01-85) — **auto-contenuti** (tutti i metadati nello YAML frontmatter)
- **85 cartelle `images_NN/`** con le foto di ogni recensione
- **778 immagini** totali
- **`_index.csv`** indice storico (non più necessario per il build — ogni `.md` è auto-contenuto)

## Ordine dei file

I file sono numerati secondo l'ordine "Data Ascendente" della tabella originale:
- `01` = più vecchia (agosto 2003)
- `85` = più recente (26 gennaio 2013)

## Formato dei file .md

Ogni file ha frontmatter YAML + corpo markdown:

```md
---
title: "Titolo Recensione"
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

Testo descrittivo...

![](images_NN/nome_immagine.jpg)

Altro testo...

![](images_NN/altra_immagine.jpg)
```

- **Frontmatter YAML** con 10 campi: title, valle, data, difficolta, periodo_consigliato, attrezzatura, tempo_di_percorrenza, dislivello, strutture, come_raggiungere
- `come_raggiungere` è multi-paragrafo (blocco YAML `|`), trimmato con narrative marker (Il sentiero, Si parte, Giunti a, ecc.)
- Le immagini sono referenziate con `![](images_NN/nome_file.jpg)` nella posizione esatta in cui comparivano nell'HTML originale
- I path delle immagini sono relativi al file .md (stessa directory)

## Script usati

Nella directory `C:\Users\Archivio\Desktop\test\`:

| Script | Scopo |
|--------|-------|
| `extract_trekking.ps1` | Estrae i link dalla pagina rece.php (primo tentativo PowerShell) |
| `convert_trekking.ps1` | Prima conversione HTML→MD (PowerShell, accenti persi) |
| `fix_markdown.ps1` | Primo cleanup formattazione |
| `fix_accents.ps1` | Tentativo fix accenti (PowerShell, problemi encoding) |
| `fix_accents.py` | Fix accenti via Python |
| `convert_all.py` | Conversione HTML→MD via Python con encoding corretto |
| `cleanup_md.py` | Cleanup formattazione markdown |
| `parse_order.py` | Parsing ordine tabella dal sito |
| `rename_and_images.py` | Rinominare file e scaricare immagini |
| `fix_missing_images.py` | Download immagini per 3 file mancanti |
| `clean_filenames.py` | Pulizia caratteri speciali nei filename |
| `rebuild_md_with_images.py` | **Script finale**: ricostruisce tutti i .md con riferimenti alle immagini |
| `download_missing_images.py` | Download immagini per recensioni 01, 11, 17 |

## Note tecniche

- Encoding originale pagine: **cp1252**
- I file .md sono salvati in **UTF-8**
- I filename sono in ASCII (caratteri accentati rimossi, sostituiti con `_`)
- Le immagini di layout (banner, bottoni, icone) sono state escluse
- Alcune immagini con spazi nell'URL non sono state scaricate (es. `foto 3.jpg` nella 54)

## Cleanup eseguito (giugno 2026)

- **Duplicati risolti**: merge immagini nei file puliti per 01, 11, 17, 75
- **`_index.csv` rigenerato**: 85 entry, encoding UTF-8 corretto
- **Formattazione**: tripli a capo e spazi iniziali rimossi da tutti i 85 file
- **YAML frontmatter**: metadati spostati da inline a frontmatter YAML per tutti i 85 file

## Generatore sito statico (`site/`)

Nella directory `C:\Users\Archivio\Desktop\test\site\`:

| File | Scopo |
|------|-------|
| `build.py` | **Script principale**: genera sito statico da `.md` (auto-contenuti, YAML frontmatter) |
| `requirements.txt` | Dipendenze Python (Jinja2, Markdown) |
| `netlify.toml` | Config deploy Netlify (`python build.py` → `output/`) |
| `templates/base.html` | Template base (header, nav, footer) |
| `templates/index.html` | Home page con griglia recensioni + filtri (valle, difficoltà, ricerca) |
| `templates/recensione.html` | Pagina singola recensione — include **meta box** automatico |
| `templates/chi-siamo.html` | Pagina Chi Siamo |
| `templates/contatti.html` | Pagina Contatti con form |
| `static/style.css` | CSS responsive, colori dal vecchio sito |
| `content/chi-siamo.md` | Contenuto Chi Siamo |
| `content/contatti.md` | Contenuto Contatti |
| `.gitignore` | Ignora `output/` |
| `verify.py` | Script di verifica |
| `recover_from_web.py` | **Recupero metadati**: estrae frontmatter YAML dal sito per tutti gli 85 file |
| `generate_frontmatter.py` | Genera frontmatter YAML da metadati inline esistenti |
| `reset_frontmatter.py` | Rimuove frontmatter (ripristino stato pulito) |

## Modifiche sessione (11 giugno 2026)

### Interfaccia home page

- **Sottotitolo hero**: `"Trekking tra Val Grande, Ossola, Verbano e valli circostanti"`
- **Logo header**: ingrandito a 100px, centrato con `justify-content: center`
- **Responsive**: breakpoint a 900px (80px), 768px (70px), 480px (55px) con `max-width: 100%`
- **Rimossa excerpt** dalle card home — ora mostrano solo Titolo, Valle, Difficoltà, Data
- **Spazio card**: margin-top footer ridotto da 1rem a 0.4rem
- **Badge difficoltà ridisegnati**:
  - T → verde (`#e6f7e6`)
  - E → rosso (`#ffe6e6`)
  - EE → rosso intenso (`#ffcccc`)
  - T/E → giallo (`#fff9cc` con bordo)
  - E/EE → rosso medio (`#ffd9d9`)
  - M/F → viola (`#f0e6ff`)
- **Accenti arancione**: nav active/hover arancione, border-bottom hero arancione, hero subtitle `#FFCC80`, btn hover arancione, back-to-top hover arancione

### Meta box recensioni (nuova feature)

- `build.py` ora **estrae automaticamente** i campi informativi dall'inizio di ogni `.md`:
  - Periodo consigliato, Attrezzatura, Tempo di percorrenza, Dislivello, Strutture, Come raggiungere
- Riconosce sia label in **grassetto** (`**Periodo consigliato**`) che **testo normale** (`consigliato :`)
- Gestisce label con a capo interni (es. `Tempo\ndi percorrenza`)
- Riconosce variante abbreviata `consigliato` → "Periodo consigliato"
- I metadati vengono rimossi dal corpo del contenuto (nessun duplicato)
- Visualizzati in un **info box** a griglia tra titolo e contenuto
- Stile: `.review-meta-box` con `grid-template-columns: repeat(auto-fit, minmax(240px, 1fr))`

### Build

- Output dir lock gestito con `try/except PermissionError` su `rmtree`
- `mkdir(parents=True, exist_ok=True)` per evitare crash

### Fix parser inline (12 giugno 2026)

- **Stray `<p>.</p>`**: `body_start_in_md` ora usa `md_text.index(body)` invece di `len(md_text) - len(body)` (il trailing `\n` nella lunghezza sballava l'offset)
- **Duplicato `Periodo consigliato`**: aggiunto negative lookbehind `(?<!Periodo\s)` al pattern `consigliato` per evitare match dentro `Periodo consigliato`
- **Multi-paragrafo "Come raggiungere"**: il parser ora estende il valore oltre `\n\n` fino al primo marcatore narrativo (`Il sentiero`, `Si parte`, `Giunti a`, `Arrivati in`, `Qui a` (non `Qui al`), `Lasciata l'auto`, ecc.) cercato entro i primi 2000 caratteri, con fallback al primo riferimento a quota `(xxxm)` o immagine `![` tramite `rfind('\n\n')`
- **`Qui\s+a(?!l\s)`**: esclude `Qui al [parola]` (direzioni) ma include `Qui all'Alpe` (narrativa)
- **Narrative marker fuori portata**: limitata ricerca marker ai primi 2000 caratteri per evitare falsi positivi (es. `Il sentiero` a metà recensione)
- **Multi-line fallback**: quota `(xxxm)` trovata su qualsiasi riga del paragrafo, non solo sulla prima dopo `\n\n`
- Testato su 84, 85, 50, 52, 06, 21, 67 — tutti OK

## Modifiche sessione (12 giugno 2026)

### YAML frontmatter (nuovo formato)

- **`recover_from_web.py`**: estrae metadati da HTML originale del sito per tutti gli 85 file (titolo da H1/H2/H3 + 6 campi informativi)
- **`generate_frontmatter.py`**: genera frontmatter YAML da metadati inline esistenti (predecessore di `recover_from_web.py`)
- **`reset_frontmatter.py`**: rimuove frontmatter per ripristino stato pulito
- `build.py` ora legge YAML frontmatter con `parse_frontmatter()`; se assente, fallback a parsing inline
- `parse_frontmatter()` mappa i key underscore (`periodo_consigliato`) ai label con spazio (`periodo consigliato`) tramite `FM_TO_LABEL`
- Nuove righe nei valori YAML collassate a spazi per evitare `<br>` spurio nell'HTML

### Fix estrazione regex in recover_from_web.py

- **Label pattern**: `\s*.*?:\s*` invece di `\s*:?\s*` — gestisce testo extra tra label e colon (es. "Come raggiungere la Val Loana :")
- **`<br>` escluso** dall'end pattern per `come_raggiungere` — cattura paragrafi multipli separati da `<br>`
- **CRLF normalization**: `\r\n` → `\n` prima del narrative marker trimming
- **Title da H2/H3**: fallback se `<h1>` assente (es. file 50 usava `<h3>`)
- **Subtitle rimosso**: tag `<br>` nell'`<h1>` tronca il titolo (es. "Pizzo d'Omo…<br>Anello turistico…" → solo "Pizzo d'Omo…")
- **Fallback filename**: se nessun heading trovato, titolo dal nome file (underscore → spazio)

### Build

- Build completo (85/85 OK) — meta box corretto per tutti i file

### File auto-contenuti (rimozione dipendenza CSV)

- **YAML frontmatter esteso**: aggiunti `valle`, `data`, `difficolta` a tutti gli 85 file (da `_index.csv`)
- **`discover_reviews()`** sostituisce `read_csv()` — scandisce il filesystem per `.md` con pattern `NN_*.md`
- Cartella immagini derivata dal numero `NN` nel filename (es. `27_*.md` → `images_27`)
- Nessuna dipendenza da `_index.csv` per il build — ogni file `.md` è completamente auto-contenuto
- Aggiungere una nuova recensione = creare un nuovo file `.md` con frontmatter + cartella immagini
- Fix YAML rotto nel file 43 (righe extra `Telefono:`/`RIFUGIO MARIA LUISA:` dentro il frontmatter)
- Fix frontmatter file 27 (mancava delimitatore `---` di chiusura)

## Come funziona

1. `build.py` scandisce `trekking_recensioni/` per file `.md` con pattern `NN_*.md`
2. Legge lo YAML frontmatter (title, valle, data, difficolta + campi informativi)
3. Deriva la cartella immagini dal numero `NN` (es. `images_27`)
4. Converte il markdown in HTML (corpo senza metadati)
5. Copia le immagini
6. Genera pagine HTML statiche in `site/output/`
7. La home ha filtri interattivi (valle, difficoltà, ricerca testo)
8. Le recensioni sono ordinate per data (dalla più recente)
9. Il build rileva automaticamente nuovi file `.md` e cartelle `images_NN/`
10. Su Netlify: `pip install -r requirements.txt && python build.py` → pubblica `output/`

## Deploy

1. Push `site/` e `trekking_recensioni/` su GitHub
2. Collega a Netlify:
   - Build command: `pip install -r requirements.txt && python build.py`
   - Publish directory: `output/`
3. Il sito si rigenera automaticamente a ogni push
