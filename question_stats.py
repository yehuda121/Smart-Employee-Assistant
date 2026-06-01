"""
Persistent tracking of successful IT Support questions for the Most Common Questions panel.
Stores only normalized keys, display text, usage counts, and insertion order — no answers or user data.

The first 10 dataset FAQ items are seeded as placeholders (count 0). Any successful question
can enter the top-10 list when its count exceeds others.
"""

import csv
import json
import logging
import os
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

STATS_DIR = Path(__file__).resolve().parent / "data"
STATS_FILE = STATS_DIR / "question_stats.json"
DATASET_FILE = Path(__file__).resolve().parent / "dataset" / "it_support_faq_dataset.csv"
TOP_QUESTIONS_LIMIT = 10

try:
    import fcntl

    _HAS_FCNTL = True
except ImportError:
    fcntl = None  # type: ignore[assignment,misc]
    _HAS_FCNTL = False


def normalize_question_key(question: str) -> str:
    """Normalize question text for counting: trim, lowercase, collapse whitespace."""
    collapsed = re.sub(r"\s+", " ", question.strip().lower())
    return collapsed


def _load_default_questions_from_dataset() -> list[dict[str, Any]]:
    """Load the first 10 FAQ questions from the IT Support dataset as initial placeholders."""
    defaults: list[dict[str, Any]] = []
    if not DATASET_FILE.exists():
        logger.error("Dataset file not found: %s", DATASET_FILE)
        return defaults

    with open(DATASET_FILE, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for order, row in enumerate(reader):
            if order >= TOP_QUESTIONS_LIMIT:
                break
            question = (row.get("question") or "").strip()
            if not question:
                continue
            defaults.append(
                {
                    "id": (row.get("id") or f"IT-{order + 1:03d}").strip(),
                    "question": question,
                    "order": order,
                }
            )
    return defaults


DEFAULT_QUESTIONS: list[dict[str, Any]] = _load_default_questions_from_dataset()


def _ensure_stats_file() -> None:
    """Create data directory and empty stats file if they do not exist."""
    STATS_DIR.mkdir(parents=True, exist_ok=True)
    if not STATS_FILE.exists():
        STATS_FILE.write_text("{}", encoding="utf-8")


def _lock_file(handle) -> None:
    if _HAS_FCNTL and fcntl is not None:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)


def _unlock_file(handle) -> None:
    if _HAS_FCNTL and fcntl is not None:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _load_stats_unlocked(handle) -> dict[str, Any]:
    handle.seek(0)
    raw = handle.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.warning("Invalid question_stats.json; resetting store: %s", exc)
        return {}
    if not isinstance(data, dict):
        logger.warning("question_stats.json root is not an object; resetting store.")
        return {}
    return data


def _save_stats_unlocked(handle, stats: dict[str, Any]) -> None:
    handle.seek(0)
    handle.truncate(0)
    json.dump(stats, handle, indent=2, ensure_ascii=False)
    handle.write("\n")
    handle.flush()
    os.fsync(handle.fileno())


def _parse_count(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _parse_order(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _max_order(stats: dict[str, Any]) -> int:
    maximum = -1
    for entry in stats.values():
        if isinstance(entry, dict) and "order" in entry:
            maximum = max(maximum, _parse_order(entry.get("order"), 0))
    return maximum


def _merge_default_entries(stats: dict[str, Any]) -> dict[str, Any]:
    """
    Seed the 10 default FAQ questions with count 0 when missing.
    Existing counts and custom questions are preserved.
    """
    merged = dict(stats)

    for item in DEFAULT_QUESTIONS:
        question = item["question"]
        key = normalize_question_key(question)
        default_order = item["order"]
        entry = merged.get(key)

        if isinstance(entry, dict):
            merged[key] = {
                "display": question,
                "count": _parse_count(entry.get("count")),
                "order": _parse_order(entry.get("order"), default_order),
            }
        else:
            merged[key] = {
                "display": question,
                "count": 0,
                "order": default_order,
            }

    return merged


def _normalize_all_entries(stats: dict[str, Any]) -> dict[str, Any]:
    """Ensure every entry has display, count, and order fields."""
    merged = _merge_default_entries(stats)
    next_order = _max_order(merged) + 1
    normalized: dict[str, Any] = {}

    for key, entry in merged.items():
        if not isinstance(entry, dict):
            continue
        display = entry.get("display")
        if not isinstance(display, str) or not display.strip():
            continue

        order = entry.get("order")
        if order is None:
            order = next_order
            next_order += 1

        normalized[key] = {
            "display": display.strip(),
            "count": _parse_count(entry.get("count")),
            "order": _parse_order(order, next_order),
        }

    return normalized


def load_stats() -> dict[str, Any]:
    """Load question statistics from disk, seeded with default FAQ placeholders."""
    _ensure_stats_file()
    with open(STATS_FILE, "r+", encoding="utf-8") as handle:
        _lock_file(handle)
        try:
            stats = _load_stats_unlocked(handle)
            merged = _normalize_all_entries(stats)
            if merged != stats:
                _save_stats_unlocked(handle, merged)
            return merged
        finally:
            _unlock_file(handle)


def record_successful_question(question: str) -> None:
    """
    Record a successful (non-fallback) question.
    Increments count for known questions; adds new questions with count 1.
    """
    key = normalize_question_key(question)
    if not key:
        return

    display = question.strip()
    _ensure_stats_file()

    with open(STATS_FILE, "r+", encoding="utf-8") as handle:
        _lock_file(handle)
        try:
            stats = _normalize_all_entries(_load_stats_unlocked(handle))
            entry = stats.get(key)

            if isinstance(entry, dict):
                entry["count"] = _parse_count(entry.get("count")) + 1
                if not entry.get("display"):
                    entry["display"] = display
            else:
                stats[key] = {
                    "display": display,
                    "count": 1,
                    "order": _max_order(stats) + 1,
                }

            _save_stats_unlocked(handle, stats)
        finally:
            _unlock_file(handle)


def get_top_questions(limit: int = TOP_QUESTIONS_LIMIT) -> list[dict[str, Any]]:
    """
    Return the top questions by usage count across all tracked questions.
    Sorted by count descending; ties preserve insertion order.
    """
    stats = load_stats()
    items: list[dict[str, Any]] = []

    for entry in stats.values():
        if not isinstance(entry, dict):
            continue
        display = entry.get("display")
        if not isinstance(display, str) or not display.strip():
            continue

        items.append(
            {
                "question": display.strip(),
                "count": _parse_count(entry.get("count")),
                "order": _parse_order(entry.get("order"), 0),
            }
        )

    items.sort(key=lambda row: (-row["count"], row["order"]))
    return [{"question": row["question"], "count": row["count"]} for row in items[:limit]]
