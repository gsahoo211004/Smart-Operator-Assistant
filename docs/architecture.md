# Architecture

## Overview

Smart Operator Assistant is a **Python + Streamlit** multipage application backed by **SQLite** and JSON seed files. Business logic lives in `src/`; UI pages live in `app/pages/`.

```
┌─────────────────────────────────────────┐
│  Streamlit (app/Home.py + pages/*.py)   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│  src/                                   │
│  data_loader · time_estimation · safety │
│  behavior · training · db               │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│  data/*.json  →  SQLite (local file)    │
└─────────────────────────────────────────┘
```

## Modules

| Module | Responsibility |
|--------|----------------|
| `db.py` | Initialize SQLite, load JSON seeds |
| `data_loader.py` | pandas access, incidents & bookings |
| `time_estimation.py` | sklearn Ridge + heuristic ETA |
| `safety.py` | Seatbelt/alerts, simulated proximity |
| `behavior.py` | Rule-based usage flags |
| `training.py` | Module catalog accessors |

## Run locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/Home.py
```

Tests: `pytest`
