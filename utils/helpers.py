"""
Miscellaneous helper utilities.
"""

from __future__ import annotations

import datetime
from typing import Any


def ts_now() -> str:
    """Return current UTC timestamp as ISO-8601 string."""
    return datetime.datetime.utcnow().isoformat(timespec="seconds")


def truncate(text: str, max_len: int = 300) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def safe_float(val: Any, default: float = 0.0) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def severity_color(score: float) -> str:
    """Map a vulnerability score (0-100) to a severity colour."""
    if score >= 80:
        return "🟢"
    if score >= 60:
        return "🟡"
    if score >= 40:
        return "🟠"
    return "🔴"


def severity_label(score: float) -> str:
    if score >= 80:
        return "Low Risk"
    if score >= 60:
        return "Medium Risk"
    if score >= 40:
        return "High Risk"
    return "Critical Risk"
