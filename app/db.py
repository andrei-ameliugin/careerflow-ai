from __future__ import annotations

import sqlite3
from pathlib import Path

from app.config import get_settings


def get_connection() -> sqlite3.Connection:
    settings = get_settings()
    Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(settings.database_path)

