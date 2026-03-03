"""
Centralised logging configuration.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)
_LOG_FILE = _LOG_DIR / "red_teaming.log"

_FORMATTER = logging.Formatter(
    "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a project-wide logger that writes to console + file."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(_FORMATTER)
    logger.addHandler(ch)

    # File handler
    fh = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    fh.setFormatter(_FORMATTER)
    logger.addHandler(fh)

    return logger
