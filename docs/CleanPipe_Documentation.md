# CleanPipe — Complete Project Documentation

> CSV Data Cleaning & ETL Pipeline
> Built with Flask + Pandas · Academic Project (CIA 3)

---

## 1. What This Document Is

This is the single, complete reference for the CleanPipe project. It explains
what the project does, how it is built, how every part works, how to run it on a
Mac (or any machine), and how to package it for submission. If you read only one
file, read this one.

---

## 2. Project Summary

**CleanPipe** turns messy CSV data into clean, usable data through a guided,
beginner-friendly workflow. Instead of being a "black box" that silently changes
your data, every step is shown to the user: what problems exist, what rules will
be applied, what will change, and what actually changed.

It demonstrates a real **ETL pipeline**:

- **Extract** — read the uploaded CSV, preserve the original.
- **Transform** — profile the data, detect issues, apply chosen cleaning rules.
- **Load** — make the cleaned CSV available to view and download, and store the run in history.

**Target users:** students, data analysts, and non-technical users who need to
clean spreadsheets without writing code.

---

## 3. The Problem It Solves

Real-world CSV files are rarely clean. Common problems:

| Problem | Example | CleanPipe's rule |
|---|---|---|
| Missing values | empty cells in a column | Fill text with `Unknown`, numbers with the column median (0 fallback) |
| Duplicate rows | the same record entered twice | Remove exact duplicate rows only |
| Extra whitespace | `" Asha "` instead of `"Asha"` | Trim leading/trailing spaces |
| Invalid dates | `"not-a-date"` in a date column | Flag for manual review (never guessed) |

Every number shown in the app comes from the user's actual uploaded file — there
are no fake metrics or demo charts.

---

## 4. Key Features

1. **Guided five-step workflow** — Upload → Understand → Choose Rules → Preview → Review. Each screen shows only what's needed for that decision.
2. **Honest data profiling** — rows, columns, missing cells per column, duplicate rows, whitespace issues, and per-column profiles (numeric / text / date).
3. **Quality score (0–100)** — combines three transparent components: completeness, uniqueness, and validity.
4. **Preview before commit** — see exactly how many cells/rows will change before anything is modified.
5. **Before vs After comparison** — side-by-side tables, original-only / cleaned-only views, and Show More.
6. **Audit trail** — every transformation logged with a reason ("Why") and an outcome.
7. **Persistent history** — each run is saved locally; survives refresh and app restart.
8. **Quality trends** — track how a dataset's quality score changes across runs.
9. **Undo / Reset** — revert the last applied cleaning, or reset back to the preserved original.
10. **Safe downloads** — download the cleaned CSV; the original is never overwritten.

---

## 5. Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask 3.0.3 (application factory pattern) |
| Data engine | Pandas 2.2.3 |
| Frontend | Jinja2 templates, vanilla CSS3, vanilla JavaScript |
| Testing | pytest 8.3.3 (8 automated tests) |
| Storage | Local filesystem (per-run folders + `history.json`) — no database |

---

## 6. Project Structure

```text
cleanpipe/
├── run.py                       # Entry point — starts the Flask server (port 3000)
├── requirements.txt             # Python dependencies
├── README.md                    # Short workflow overview
├── plan.md                      # Original design/implementation plan
├── TODO.md                      # Delivery checklist (all items done)
├── CleanPipe_Report.md          # Short summary report
├── CleanPipe_Documentation.md   # THIS FILE — full documentation
├── CleanPipe_Presentation.pdf   # Project slides
│
├── app/
│   ├── __init__.py              # create_app() application factory + config
│   ├── routes.py                # All HTTP routes (landing, dashboard, upload, clean, results, download)
│   ├── services/
│   │   └── pipeline.py          # Core Pandas logic: load, profile, clean, quality, audit
│   ├── templates/               # Jinja2 HTML (base, landing, dashboard, upload, workflow, cleaning, results)
│   └── static/
│       ├── css/app.css          # Stylesheet
│       └── js/                  # app.js, cleaning.js, trends.js (view switching, preview)
│
├── sample_data/
│   ├── sample_dataset.csv       # Real messy sample (missing values, duplicates, whitespace)
│   └── missing_values_test.csv  # Extra test dataset
│
├── tests/
│   └── test_cleanpipe.py        # 8 automated tests
│
└── instance/                    # Runtime data (per-run CSVs, reports, history.json) — git-ignored
```

---

## 7. How It Works (Architecture)

### 7.1 Request flow

```
Browser ──HTTP──▶ Flask routes (routes.py) ──▶ pipeline.py (Pandas) ──▶ instance/runs/<id>/
                        │                                                      │
                        └──────── Jinja templates render the result ◀─────────┘
```

### 7.2 The ETL stages (shown in the UI as a pipeline strip)

1. **Extract** — `load_csv()` validates extension, non-empty content, and readable structure, then reads the file into a DataFrame. The original is saved untouched as `original.csv`.
2. **Profile** — `profile_dataset()` computes rows, columns, missing cells, duplicates, whitespace, per-column profiles, quality score, and a detected-issues list.
3. **Transform** — `clean_dataset()` applies only the rules the user selected.
4. **Validate** — quality score and issue checks run on the cleaned data.
5. **Load** — the cleaned CSV is written and offered for view/download; the run is recorded in `history.json`.

### 7.3 Per-run storage

Each upload gets a unique 10-character run id and its own folder under
`instance/runs/<run_id>/`:

- `original.csv` — the preserved upload (never modified)
- `cleaned.csv` — the cleaned output
- `working.csv` — current working copy
- `undo.csv` — snapshot for undo
- `profile.json` — profiling result
- `report.json` — before/after report and audit trail

`instance/history.json` indexes every run so the dashboard and results stay
available after a refresh or an app restart.

---

## 8. Core Logic — `app/services/pipeline.py`

| Function | Responsibility |
|---|---|
| `load_csv(path)` | Validate `.csv` extension, non-empty, readable structure; return a DataFrame or raise a user-friendly `DataError`. |
| `profile_dataset(frame)` | Produce the full profile: counts, per-column missing/whitespace, preview rows, quality, issues, column profiles. |
| `profile_columns(frame)` | Per-column stats: dtype, missing, unique, numeric min/max/mean/median, top text values, date ranges. |
| `quality_metrics(frame)` | Compute completeness, uniqueness, validity, and an overall 0–100 score. |
| `detect_issues(frame)` | Build the explainable issue list (missing, duplicates, whitespace, invalid dates). |
| `clean_dataset(frame, operations)` | Apply selected rules (trim, fill, dedupe), build the before/after report + audit trail. |
| `issue_resolution(before, after)` | Compare issues before vs after to show what was fixed vs what remains. |
| `read_saved_report(dir, run_id)` | Load a saved `report.json` for reopening a past run. |

### 8.1 Quality score definition

```
completeness = (non-empty cells / total cells) × 100
uniqueness   = (unique rows / total rows) × 100
validity     = (valid dates / total date values) × 100   (only if a date column exists)
overall      = average of the available components, rounded to 2 decimals
```

### 8.2 Cleaning rules (exact behaviour)

- **Trim whitespace** — strip leading/trailing spaces from text cells.
- **Fill missing text** — replace empty text with `Unknown`.
- **Fill missing numeric** — replace empty numbers with the column **median**; if no numeric values exist at all, use `0` as a documented fallback.
- **Remove duplicates** — drop only **exact** duplicate rows.
- **Invalid dates** — never guessed; flagged for manual review.

---

## 9. Routes Reference — `app/routes.py`

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Landing page |
| GET | `/dashboard` | History + quality trends (optional `?dataset=` filter) |
| GET/POST | `/upload` | Upload a CSV; validates and starts a run |
| GET | `/clean/<run_id>` | Cleaning workflow (understand step) |
| GET | `/workflow/<run_id>/<step>` | A focused workflow step: `understand` / `rules` / `preview` |
| POST | `/clean/<run_id>` | Apply selected cleaning rules |
| POST | `/clean/<run_id>/preview` | JSON preview of predicted changes (no modification) |
| POST | `/clean/<run_id>/reset` | Reset working data back to the original |
| POST | `/clean/<run_id>/undo` | Undo the last applied cleaning |
| GET | `/results/<run_id>` | Before/after results, audit trail, comparison |
| GET | `/download/cleaned/<run_id>` | Download the cleaned CSV |
| GET | `/sample.csv` | Download the bundled sample dataset |

---

## 10. How to Run It Locally (macOS)

### Prerequisites
- Python 3.10+ (tested on Python 3.12). Check with:
  ```bash
  python3 --version
  ```

### Step 1 — Open the project
```bash
cd ~/Desktop/cleanpipe
```

### Step 2 — (Recommended) Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Run the app
```bash
python3 run.py
```

### Step 5 — Open in a browser
Go to: **http://127.0.0.1:3000**

To stop the server, press `Ctrl + C` in the terminal.

### Try it
1. Click through to **Upload** and choose `sample_data/sample_dataset.csv`
   (or download the sample from the app).
2. Inspect the detected issues on the **Understand** step.
3. Choose rules, **Preview**, then apply.
4. Compare before/after and **download** the cleaned CSV.

---

## 11. How to Run the Tests

```bash
cd ~/Desktop/cleanpipe
python3 -m pytest tests/ -v
```

Expected: **8 passed**. The suite covers:

- Landing page and empty dashboard
- Full end-to-end run (upload → clean → results → download) + history persistence across restart
- A second valid CSV and invalid inputs (wrong extension, empty file)
- Quality trends using saved scores and issue counts, with a dataset filter
- Graceful handling of older reports missing newer metrics
- Actual profiling and cleaning rule correctness
- Quality scores + audit trail from real values
- Column profiler, preview, selective cleaning, undo, and reset

---

## 12. Verification (performed on this machine)

- Python: `3.12.2` (Anaconda)
- `pip install -r requirements.txt` → installed Flask 3.0.3, pandas 2.2.3, pytest 8.3.3
- `python3 -m pytest tests/ -v` → **8 passed**
- `python3 run.py` → server started on port 3000
- Route checks (HTTP status):
  - `/` → 200
  - `/dashboard` → 200
  - `/upload` → 200
  - `/sample.csv` → 200

---

## 13. CIA 3 Submission Checklist

The submission ZIP must contain the following (per the assignment):

- [x] **Complete project code** — the entire `app/`, `tests/`, `run.py`, `requirements.txt`, `sample_data/`.
- [x] **Project presentation** — `CleanPipe_Presentation.pdf`.
- [x] **Brief report** — `CleanPipe_Report.md` (short) and `CleanPipe_Documentation.md` (full, this file).

**Deadline:** 25 October 2026 · **CIA 3 date:** 26 October 2026.

### Recommended ZIP contents
```
CleanPipe_Submission.zip
├── app/
├── tests/
├── sample_data/
├── run.py
├── requirements.txt
├── README.md
├── CleanPipe_Report.md
├── CleanPipe_Documentation.md
└── CleanPipe_Presentation.pdf
```
> Tip: exclude `instance/`, `__pycache__/`, and `.venv/` from the ZIP — they are
> runtime/generated files and not part of the source.

---

## 14. Quick Command Cheat-Sheet

```bash
# Setup
cd ~/Desktop/cleanpipe
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run
python3 run.py            # then open http://127.0.0.1:3000

# Test
python3 -m pytest tests/ -v

# Package for submission (from inside the cleanpipe folder)
zip -r CleanPipe_Submission.zip app tests sample_data run.py \
  requirements.txt README.md CleanPipe_Report.md \
  CleanPipe_Documentation.md CleanPipe_Presentation.pdf
```

---

*CleanPipe · Academic Project Submission · 2026*
