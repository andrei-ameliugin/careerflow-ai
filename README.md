# CareerFlow AI

CareerFlow AI is a local-first single-user Python application for smart job discovery and semi-automated applications on `hh.ru`.

This repository currently contains the initial project skeleton for Phase 1. The goal of this step is to keep the project simple, runnable, and ready for incremental development.

## Stack

- Python 3.12+
- Streamlit
- SQLite

## Project Layout

```text
app/      Application package
data/     Local SQLite database and other local runtime data
scripts/  Small helper scripts
tests/    Smoke tests
```

## Run

Create a virtual environment, install the package, and start Streamlit:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
streamlit run streamlit_app.py
```

## Test

```bash
python -m pytest
```
