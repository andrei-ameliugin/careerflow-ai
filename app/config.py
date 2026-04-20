from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "CareerFlow AI"
    database_path: Path = Path("data") / "careerflow.db"


def get_settings() -> Settings:
    return Settings()

