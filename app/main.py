from __future__ import annotations

import streamlit as st

from app.config import get_settings
from app.db import SessionLocal, init_db


def main() -> None:
    settings = get_settings()

    st.set_page_config(page_title=settings.app_name, layout="wide")
    st.title(settings.app_name)
    st.caption("Phase 1 skeleton for a local-first hh.ru assistant")

    init_db()
    session = SessionLocal()
    try:
        st.success("SQLite database initialized")
        st.write(f"Database path: `{settings.database_path}`")
    finally:
        session.close()


if __name__ == "__main__":
    main()
