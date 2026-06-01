"""
Persistent tracking of successful IT Support questions for the Most Common Questions panel.
Stores only normalized keys, display text, and counts — no answers or user data.

The panel always shows exactly 10 pre-defined FAQ questions from the dataset (IT-001–IT-010).
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
    """Load the first 10 FAQ questions from the IT Support dataset."""
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
DEFAULT_QUESTION_KEYS: frozenset[str] = frozenset(
    normalize_question_key(item["question"])
    for item in DEFAULT_QUESTIONS
    if item.get("question")
)


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


def _merge_default_entries(stats: dict[str, Any]) -> dict[str, Any]:
    """
    Ensure all 10 default FAQ questions exist in stats with count >= 0.
    Display text always follows the dataset wording.
    """
    merged = dict(stats)
    for item in DEFAULT_QUESTIONS:
        question = item["question"]
        key = normalize_question_key(question)
        entry = merged.get(key)
        if isinstance(entry, dict):
            count = entry.get("count", 0)
            try:
                count_int = max(0, int(count))
            except (TypeError, ValueError):
                count_int = 0
            merged[key] = {"display": question, "count": count_int}
        else:
            merged[key] = {"display": question, "count": 0}
    return merged


def load_stats() -> dict[str, Any]:
    """Load question statistics from disk, merged with default FAQ entries."""
    _ensure_stats_file()
    with open(STATS_FILE, "r+", encoding="utf-8") as handle:
        _lock_file(handle)
        try:
            stats = _load_stats_unlocked(handle)
            merged = _merge_default_entries(stats)
            if merged != stats:
                _save_stats_unlocked(handle, merged)
            return merged
        finally:
            _unlock_file(handle)


def record_successful_question(question: str) -> None:
    """
    Increment count when a default FAQ question receives a successful answer.
    Only the 10 pre-defined dataset questions are tracked for the panel.
    """
    key = normalize_question_key(question)
    if not key or key not in DEFAULT_QUESTION_KEYS:
        return

    _ensure_stats_file()
    with open(STATS_FILE, "r+", encoding="utf-8") as handle:
        _lock_file(handle)
        try:
            stats = _merge_default_entries(_load_stats_unlocked(handle))
            entry = stats[key]
            entry["count"] = int(entry.get("count", 0)) + 1
            _save_stats_unlocked(handle, stats)
        finally:
            _unlock_file(handle)


def get_top_questions(limit: int = TOP_QUESTIONS_LIMIT) -> list[dict[str, Any]]:
    """
    Return exactly 10 default FAQ questions with usage counts.
    Sorted by count descending; ties preserve original dataset order.
    """
    stats = load_stats()
    items: list[dict[str, Any]] = []

    for item in DEFAULT_QUESTIONS:
        question = item["question"]
        key = normalize_question_key(question)
        entry = stats.get(key, {})
        count = 0
        if isinstance(entry, dict):
            try:
                count = max(0, int(entry.get("count", 0)))
            except (TypeError, ValueError):
                count = 0

        items.append(
            {
                "question": question,
                "count": count,
                "order": item["order"],
            }
        )

    items.sort(key=lambda row: (-row["count"], row["order"]))
    return [{"question": row["question"], "count": row["count"]} for row in items[:limit]]
