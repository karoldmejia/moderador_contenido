# Social Media Content Moderator


## Team:
- Johan S. Guzmán - A00401480
- Karold L. Mejia - A00401806


> A simple, didactic content‑moderation demo that detects **spam**, **offensive/sexual/violent language**, and **harassment/threats**, censors disallowed tokens **while preserving length**, and gently **post‑processes** user text (links, @mentions, #hashtags, emoji, and inline LaTeX) — all wrapped in a minimal **Flask** web UI.

---

## Project overview

This repository implements a modular text‑moderation pipeline built from classic **finite‑state machines**:

- **DFAs** (`SpamDFA`, `ContentDFA`, `DirectionalityDFA`) to classify input by category and direction (self vs. others vs. generic).
- **FSTs** (`CensorshipFST`, `WarningFST`) to transform text (length‑preserving masking) and to map final DFA states to readable warnings.
- A **post‑processor** (`post_processor.py`) that lightly enhances the rendered text (links/mentions/hashtags/emoji) and supports a tiny **textX** grammar (`post.tx`) to keep inline math (e.g., `$\frac{1}{2}$`) intact. The UI renders math with **MathJax**.

The web app exposes two pages:
- `GET /` – main form to analyze text and preview the transformed post + warnings
- `GET /details` – developer‑friendly, step‑by‑step trace of the pipeline

---

## Project structure

```text
moderador_contenido
├── .vscode
│   └── settings.json
├── docs
│   ├── Desing (Graphs)
│   │   ├── censorship_fst.png
│   │   ├── content_dfa.png
│   │   ├── directionality_dfa.png
│   │   ├── formalDefinitionDFA.png
│   │   ├── spam_dfa.png
│   │   └── warning_fst.png
│   ├── Modules Design
│   │   ├── CensorshipFST_Module_Design.md
│   │   ├── ContentDFA_Module_Design.md
│   │   ├── DirectionalityDFA_Module_Design.md
│   │   ├── PostTransform_Module_Design.md
│   │   ├── Preprocessing_Module_Design.md
│   │   ├── SpamDFA_Module_Design.md
│   │   ├── TextPipeline_Module_Design.md
│   │   └── WarningFST_Module_Design.md
│   ├── Tests Design
│   │   ├── Test_Design_CensorshipFST.md
│   │   ├── Test_Design_ContentDFA.md
│   │   ├── Test_Design_DirectionalityDFA.md
│   │   ├── Test_Design_PostProcessor.md
│   │   ├── Test_Design_Prepocessing.md
│   │   ├── Test_Design_SpamDFA.md
│   │   ├── Test_Design_TextPipeline.md
│   │   └── Test_Design_WarningFST.md
│   ├── formal_definition_dfa.md
│   └── formal_definition_fst.md
├── src
│   ├── __init__.py
│   ├── censorship_fst.py
│   ├── content_dfa.py
│   ├── data
│   │   └── keywords.json
│   ├── directionality_dfa.py
│   ├── pipeline.py
│   ├── post.tx
│   ├── post_processor.py
│   ├── preprocessing.py
│   ├── spam_dfa.py
│   └── warning_fst.py
├── static
│   ├── icons
│   │   └── warning.png
│   └── style.css
├── templates
│   ├── details.html
│   └── index.html
├── tests
│   ├── __init__.py
│   ├── test_censorship_fst.py
│   ├── test_content_dfa.py
│   ├── test_directionality_dfa.py
│   ├── test_pipeline.py
│   ├── test_post_processor.py
│   ├── test_preprocessing.py
│   ├── test_spam_dfa.py
│   └── test_warning_fst.py
├── app.py
├── README.md
└── requirements.txt
```

---

## Installation

### 1. Prerequisites
- Python **3.11+** (project artifacts show 3.11/3.12 bytecode in `__pycache__`)
- pip

### 2. Clone & enter the project
```bash
git clone https://github.com/Bloque-CED/ti1-2025-2-hott_peolple.git
cd ti1-2025-2-hott_peolple
```

### 3. Create and activate a virtual environment
```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies
The provided `requirements.txt` is **UTF‑16 LE**. Two options:


```bash
pip install -r requirements.txt

```

---

## How to run the project

### Run with Python directly (recommended for local dev)
```bash
python app.py
```
This starts Flask in debug mode on **http://127.0.0.1:5000/**.

### Alternative: Flask CLI
```bash
flask --app app run --debug
```

---

## Testing

Unit tests live under `tests/` and use **pytest**. You can check the tests running:

```bash
pytest tests
```

---

## Requirements

From `requirements.txt`:

- `Arpeggio==2.0.3`
- `blinker==1.9.0`
- `click==8.3.0`
- `colorama==0.4.6`
- `coverage==7.10.7`
- `Flask==3.1.2`
- `iniconfig==2.1.0`
- `itsdangerous==2.2.0`
- `Jinja2==3.1.6`
- `MarkupSafe==3.0.3`
- `packaging==25.0`
- `pluggy==1.6.0`
- `Pygments==2.19.2`
- `pyparsing==3.2.5`
- `pytest==8.4.2`
- `pytest-cov==7.0.0`
- `textX==4.2.2`
- `Werkzeug==3.1.3`

---

## Usage examples

### 1. Use the web UI
1. Start the server (see **How to run**).
2. Open **http://127.0.0.1:5000/** in your browser.
3. Paste a message and click **Analyze**.
4. Review:
   - **Processed post** (with links/mentions/hashtags and inline `$...$` rendered)
   - **Warnings** (e.g., “this post may contain offensive language”)

Try:
```
Hey @karol check this link https://example.com #sunset :-)
I feel so dumb today… but $\frac{1}{2}$ still equals 0.5!
```
---

## Technologies used

- **Python / Flask / Jinja2** — web server and templates
- **Finite‑state machines** — DFAs for classification; FSTs for transformations
- **textX** (`post.tx`) and **Arpeggio** — tiny grammar to protect inline math
- **MathJax** — client‑side rendering of `$...$` in the browser
- **Pytest / pytest‑cov** — testing and coverage
- **CSS** (`static/style.css`) + Google Fonts + Material Symbols — minimal UI

---

### 📎 Appendix: Where things happen

- **Entry point**: `app.py` (Flask app; routes `/` and `/details`).
- **Core pipeline**: `src/pipeline.py` — orchestrates tokenization, DFAs/FSTs, post‑processing.
- **Keywords**: `src/data/keywords.json` — word lists for categories and spam.
- **DFAs**: `src/spam_dfa.py`, `src/content_dfa.py`, `src/directionality_dfa.py`.
- **FSTs**: `src/censorship_fst.py`, `src/warning_fst.py`.
- **Post‑processing**: `src/post_processor.py` (+ grammar in `src/post.tx`).


This project was developed as part of the Computation and Discrete Structures 3 course, academic term 2025-2