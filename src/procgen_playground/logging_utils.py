"""Bounded, per-user logs also capture upstream's console output in windowed builds."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys


def log_directory() -> Path:
    local = os.environ.get("LOCALAPPDATA")
    root = Path(local) if local else Path.home() / "AppData" / "Local"
    return root / "ProcGenPlayground" / "logs"


class LogStream:
    def __init__(self, level: int) -> None:
        self.level = level

    def write(self, text: str) -> int:
        for line in text.splitlines():
            if line.strip():
                logging.getLogger("upstream").log(self.level, line)
        return len(text)

    def flush(self) -> None:
        for handler in logging.getLogger().handlers:
            handler.flush()


def configure_logging(role: str = "playground") -> Path:
    directory = log_directory()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{role}.log"
    handler = RotatingFileHandler(path, maxBytes=2_000_000, backupCount=2, encoding="utf-8")
    logging.basicConfig(level=logging.INFO, handlers=[handler],
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s", force=True)
    if sys.stdout is None or getattr(sys, "frozen", False):
        sys.stdout = LogStream(logging.INFO)
    if sys.stderr is None or getattr(sys, "frozen", False):
        sys.stderr = LogStream(logging.WARNING)
    return path
