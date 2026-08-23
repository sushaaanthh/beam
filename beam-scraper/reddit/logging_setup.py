"""Structured logging for the scraper.

Console: concise human-readable lines.
File (logs/scraper.log): one JSON object per line with message + extras.
Credentials are never passed through `extra` and never logged.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

RESERVED = set(vars(logging.LogRecord("", 0, "", 0, "", (), None)).keys()) | {
    "message",
    "asctime",
    "taskName",
}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "event": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in RESERVED and not key.startswith("_"):
                try:
                    json.dumps(value)
                    payload[key] = value
                except (TypeError, ValueError):
                    payload[key] = repr(value)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO", log_dir: str | Path = "logs") -> None:
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers.clear()

    console = logging.StreamHandler()
    console.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)-7s %(name)s %(message)s", "%H:%M:%S")
    )
    root.addHandler(console)

    file_handler = RotatingFileHandler(
        log_dir_path / "scraper.log",
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(JsonFormatter())
    root.addHandler(file_handler)
