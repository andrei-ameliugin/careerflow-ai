from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import get_settings

LOGGER_NAME = "careerflow"
LOG_FILE_NAME = "app.log"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger

    settings = get_settings()
    log_dir = Path(settings.DATA_DIR) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / LOG_FILE_NAME

    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=1_048_576,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    configure_logging()
    if not name:
        return logging.getLogger(LOGGER_NAME)
    return logging.getLogger(f"{LOGGER_NAME}.{name}")
