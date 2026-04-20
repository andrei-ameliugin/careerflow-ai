# CareerFlow AI

CareerFlow AI is a local-first single-user Streamlit app for building and reviewing candidate profile data for `hh.ru` workflows.

## Current MVP

The current application supports only these features:

- Create and list profiles
- Save an optional `hh.ru` resume URL per profile
- Add resume content in the wizard by pasting text or uploading a file
- Save deep-context wizard answers for a selected profile
- View profile details, saved resume assets, wizard answers, generated facts, and runs
- Create draft runs for a profile
- Initialize and store data locally in SQLite

## Tech Stack

- Python 3.12+
- Streamlit
- SQLite
- SQLAlchemy
- Pytest

## Project Layout

```text
app/      Application package
data/     Local SQLite database and runtime data
pages/    Streamlit pages
scripts/  Small helper scripts
tests/    Automated tests
```

## Local Setup

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -e .
```

### 3. Create a local `.env` file

Create `.env` in the project root with the current required settings:

```env
APP_ENV=local
DATA_DIR=data
DATABASE_URL=sqlite:///data/careerflow.db
AI_PROVIDER_API_KEY=dev-local-key
```

Notes:

- `DATABASE_URL` points to the local SQLite database file
- `DATA_DIR` is used for local app data such as the database and logs
- `AI_PROVIDER_API_KEY` is currently a placeholder setting for local development

### 4. Initialize the database

```bash
python3 -m app.cli init-db
```

### 5. Run the Streamlit app

```bash
streamlit run streamlit_app.py
```

Then open the local Streamlit URL shown in the terminal.

## Running Tests

Run the test suite with:

```bash
python3 -m pytest
```

## Typical Local Workflow

```bash
source .venv/bin/activate
python3 -m app.cli init-db
streamlit run streamlit_app.py
```
