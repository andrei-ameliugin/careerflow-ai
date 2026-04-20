from __future__ import annotations

import streamlit as st

from app.config import get_settings
from app.db import init_db


def main() -> None:
    settings = get_settings()

    st.set_page_config(page_title=settings.app_name, layout="wide")
    init_db()

    st.title(settings.app_name)
    st.caption("Local-first hh.ru assistant")
    st.write("Use the sidebar to open the Profiles page.")


if __name__ == "__main__":
    main()
