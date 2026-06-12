# ScioccoBlocco — Trekking & Bike

[![Netlify Status](https://api.netlify.com/api/v1/badges/.../deploy-status)](https://scioccoblocco.com)

> **Trekking tra Val Grande, Ossola, Verbano e valli circostanti.**  
> Oltre 80 itinerari recuperati da un forum storico del web, trasformati in un sito statico moderno e accessibile.

Un archivio vivo di recensioni escursionistiche scritte da una piccola comunità nata sulle rive del Lago Maggiore. Ogni itinerario è stato estratto dal vecchio sito, convertito in Markdown con immagini, e pubblicato come sito statico generato da Python.

**URL:** [https://scioccoblocco.com](https://scioccoblocco.com)

---

## Indice

- [Panoramica](#panoramica)
- [Struttura del progetto](#struttura-del-progetto)
- [Come funziona](#come-funziona)
- [Formato recensioni](#formato-recensioni)
- [Build e deploy](#build-e-deploy)
- [Requisiti](#requisiti)
- [Sviluppo locale](#sviluppo-locale)
- [Aggiungere una nuova recensione](#aggiungere-una-nuova-recensione)
- [Script di recupero](#script-di-recupero)
- [Storia](#storia)
- [Licenza](#licenza)

---

## Panoramica

ScioccoBlocco era un forum italiano attivo nei primi anni 2000, centrato sul Verbano Cusio Ossola. Tra discussioni, viaggi e passioni, gli utenti pubblicavano dettagliate **recensioni di trekking** con foto dei percorsi. Questo progetto recupera, preserva e rende nuovamente accessibili quelle 85 recensioni, trasformandole in un **sito statico** moderno:

- **85 recensioni** (da agosto 2003 a gennaio 2013)
- **778 immagini** originali
- **20+ valli** coperte (Val Grande, Valle Ossola, Valle Strona, Val Formazza, Val di Devero, ecc.)
- Difficoltà: T (Turistica), E (Escursionistica), EE (Escursionismo Esperto), e varianti

Ogni recensione è **auto-contenuta**: il file Markdown include frontmatter YAML con tutti i metadati (titolo, valle, data, difficoltà, periodo consigliato, attrezzatura, tempo, dislivello, strutture, come raggiungere) più il corpo del testo con le immagini referenziate localmente.

---

## Struttura del progetto

```
scioccoblocco/
├── build.py                    # Generatore sito statico (Python)
├── requirements.txt            # Dipendenze Python
├── netlify.toml                # Configurazione deploy Netlify
├── .gitignore
├── AGENTS.md                   # Documentazione tecnica interna
│
├── trekking_recensioni/        # Recensioni in Markdown (85 file)
│   ├── 01_Cicogna-Alpe_Pre-Pogallo-Cicogna.md
│   ├── 02_Archia-Monte_Zeda-Sentiero_Cadorna.md
│   ├── ...
│   ├── 85_Rifugio_Gattascosa_(CIASPOLE).md
│   ├── _index.csv              # Indice storico (non più necessario per il build)
│   ├── images_01/              # Foto della recensione 01
│   ├── images_02/
│   └── ...
│
├── templates/                  # Template Jinja2
│   ├── base.html               # Base (header, nav, footer)
│   ├── index.html              # Home con griglia recensioni + filtri
│   ├── recensione.html         # Pagina singola recensione
│   ├── chi-siamo.html          # Pagina Chi Siamo
│   └── contatti.html           # Pagina Contatti
│
├── static/                     # Asset statici
│   ├── style.css               # CSS responsive
│   ├── banner_rece.jpg
│   └── 1bg_top_03.gif          # Logo storico
│
├── content/                    # Pagine di contenuto in Markdown
│   ├── chi-siamo.md
│   └── contatti.md
│
└── dist/                       # Output del build (generato, in .gitignore)
    ├── index.html
    ├── recensioni/
    ├── chi-siamo/
    ├── contatti/
    └── static/
```

---

## Come funziona

1. **`build.py`** scandisce `trekking_recensioni/` e trova tutti i file `.md` con pattern `NN_Nome.md`
2. Legge lo **YAML frontmatter** di ogni file per estrarre titolo, valle, data, difficoltà e campi informativi
3. Deriva automaticamente la cartella immagini dal numero `NN` (es. `27_*.md` → `images_27`)
4. Converte il corpo Markdown in HTML usando la libreria `markdown`
5. Copia le immagini in ogni pagina di destinazione
6. Genera pagine HTML statiche in `dist/` usando i **template Jinja2**
7. La **home page** ha filtri interattivi per valle, difficoltà e ricerca testo
8. Le recensioni sono ordinate per data (dalla più recente)
9. Le pagine "Chi Siamo" e "Contatti" sono generate da file Markdown

### Filtri home page

Il sito frontend (zero dipendenze JS) permette filtraggio lato client per:
- **Valle** (dropdown)
- **Difficoltà** (dropdown con T/E/EE/MF)
- **Testo** (ricerca nel nome del percorso)

### Pagina recensione

Ogni recensione mostra:
- Titolo, valle, data, difficoltà (badge colorati)
- **Meta box informativo** con: periodo consigliato, attrezzatura, tempo di percorrenza, dislivello, strutture, come raggiungere
- Corpo del testo con immagini posizionate dove comparivano nell'originale

---

## Formato recensioni

Ogni file Markdown è **auto-contenuto** con frontmatter YAML:

```yaml
---
title: "Cicogna- Alpe Prà (Alpino)-Pogallo-Cicogna"
valle: Val Grande
data: "agosto 2003"
difficolta: E
periodo_consigliato: da aprile a novembre
attrezzatura: |
  comode scarpe da montagna e abbigliamento sportivo
tempo_di_percorrenza: 4.30h/5.00h
dislivello: |
  Totale 1158 m
strutture: |
  Circolo ARCI "F.Cavallotti" Cicogna tel. 0323/581712
come_raggiungere: |
  Da Intra andare a Trobaso quindi proseguire per la strada che porta a Bieno...
---
```

### Campi frontmatter

| Campo | Descrizione |
|-------|-------------|
| `title` | Nome dell'itinerario |
| `valle` | Valle di appartenenza |
| `data` | Data dell'escursione |
| `difficolta` | T, E, EE, T/E, E/EE, M/F |
| `periodo_consigliato` | Periodo dell'anno consigliato |
| `attrezzatura` | Equipaggiamento suggerito |
| `tempo_di_percorrenza` | Durata dell'itinerario |
| `dislivello` | Dislivello totale |
| `strutture` | Rifugi, punti di appoggio |
| `come_raggiungere` | Come arrivare al punto di partenza |

---

## Build e deploy

### Netlify (produzione)

Il progetto è configurato per il deploy su Netlify tramite `netlify.toml`:

```toml
[build]
  command = "pip install -r requirements.txt && python build.py"
  publish = "dist"

[build.environment]
  PYTHON_VERSION = "3.10"
```

1. Push del repository su GitHub
2. Collega a Netlify
3. Il build command e publish directory sono già configurati
4. Il sito si rigenera automaticamente a ogni push

### Locale

```bash
pip install -r requirements.txt
python build.py
```

Il sito viene generato in `dist/`. Apri `dist/index.html` nel browser.

---

## Requisiti

- Python 3.10+
- Dipendenze (vedi `requirements.txt`):
  - `Jinja2>=3.0` — template engine
  - `Markdown>=3.0` — conversione Markdown → HTML
  - `PyYAML>=6.0` — parsing YAML frontmatter

---

## Sviluppo locale

```bash
# Clona il repository
git clone https://github.com/tuo-utente/scioccoblocco.git
cd scioccoblocco

# Installa dipendenze
pip install -r requirements.txt

# Build
python build.py

# Apri in browser
start dist/index.html
```

---

## Aggiungere una nuova recensione

1. Crea un file `{numero}_{Nome_Recensione}.md` in `trekking_recensioni/` con frontmatter YAML completo (vedi [formato](#formato-recensioni))
2. Crea una cartella `images_{numero:02d}/` con le foto
3. Riferisci le immagini nel Markdown come `![](images_NN/nome_file.jpg)`
4. Esegui `python build.py` — il build rileva automaticamente il nuovo file

**Nessuna modifica a script o configurazioni è necessaria**: il build scandisce il filesystem e ogni file `.md` è auto-contenuto.

---

## Script di recupero

Nella directory `C:\Users\Archivio\Desktop\test\` (storico, non inclusa nel repository) sono conservati gli script usati per l'estrazione e la conversione dal vecchio sito:

| Script | Scopo |
|--------|-------|
| `extract_trekking.ps1` | Estrazione link dalla pagina `rece.php` |
| `convert_all.py` | Conversione HTML→Markdown con encoding cp1252 |
| `rebuild_md_with_images.py` | Ricostruzione file .md con riferimenti immagini |
| `recover_from_web.py` | Recupero metadati dal sito originale |
| `cleanup_md.py` | Pulizia formattazione markdown |
| `rename_and_images.py` | Rinomina file e download immagini |

Questi script hanno prodotto i 85 file `.md` e le 778 immagini presenti in `trekking_recensioni/`.

---

## Storia

ScioccoBlocco nasce nei primi anni 2000 come forum di una piccola comunità del Verbano Cusio Ossola. Per anni è stato un punto di incontro per scambiare idee, opinioni e passioni: libri, musica, film, viaggi e soprattutto **trekking** tra Val Grande, Ossola e Valle Strona.

Con la chiusura del forum originale, le recensioni — scritte con cura e passione da utenti come **Bilbo**, **Forte**, **Daja**, **Homer**, **Witness**, **Capitano MTB**, **Buffalo_666**, **Pollon**, **Kakomi** e **Show** — rischiavano di andare perdute. Questo progetto le recupera, le preserva e le rende nuovamente accessibili in un formato moderno.

---

## Licenza

Il contenuto testuale delle recensioni appartiene agli autori originali. Il codice del generatore del sito è distribuito sotto licenza MIT.
