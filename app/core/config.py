from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "local"
    DATA_DIR: Path = Path("data")
    DATABASE_URL: str = "sqlite:///data/careerflow.db"
    AI_PROVIDER_API_KEY: str = "dev-local-key"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def app_name(self) -> str:
        return "CareerFlow AI"

    @property
    def database_path(self) -> Path:
        sqlite_prefix = "sqlite:///"
        if self.DATABASE_URL.startswith(sqlite_prefix):
            return Path(self.DATABASE_URL.removeprefix(sqlite_prefix))
        return self.DATA_DIR / "careerflow.db"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
