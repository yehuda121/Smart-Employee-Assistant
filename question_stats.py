"""
Popular question tracking for the Most Common Questions panel using Amazon DynamoDB.
Stores question text, normalized form, usage counts, and fallback counts — no answers or user data.
"""

import hashlib
import logging
import re
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from aws_config import get_upload_account_config

logger = logging.getLogger(__name__)

TOP_QUESTIONS_LIMIT = 10
ENTITY_TYPE_QUESTION = "QUESTION"
ENTITY_TYPE_SYSTEM = "SYSTEM"
KB_SYNC_STATUS_ID = "SYSTEM#KB_SYNC_STATUS"

SORT_POPULAR = "popular"
SORT_RECENT = "recent"
SORT_FALLBACKS = "fallbacks"

SEED_QUESTIONS: tuple[str, ...] = (
    "How do I reset my password?",
    "How do I request VPN access?",
    "How do I set up MFA?",
    "How do I install approved software?",
    "How do I request a new laptop?",
    "How do I configure Outlook email?",
    "How do I access SharePoint?",
    "How do I connect to office WiFi?",
    "How do I request production access?",
    "How do I open an IT support ticket?",
)

_dynamodb_table = None
_seed_attempted = False


def normalize_question_key(question: str) -> str:
    """Normalize question text: trim, lowercase, collapse whitespace."""
    return re.sub(r"\s+", " ", question.strip().lower())


def _question_id(normalized: str) -> str:
    """Stable partition key from normalized question text."""
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_credentials() -> tuple[str, str, str]:
    config = get_upload_account_config()
    return (
        config["ACTIVE_AWS_REGION"],
        config["AWS_ACCESS_KEY_ID"],
        config["AWS_SECRET_ACCESS_KEY"],
    )


def _get_table():
    """Return the configured DynamoDB table."""
    global _dynamodb_table
    if _dynamodb_table is not None:
        return _dynamodb_table

    config = get_upload_account_config()
    region, access_key, secret_key = _get_credentials()

    dynamodb = boto3.resource(
        "dynamodb",
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    _dynamodb_table = dynamodb.Table(config["ACTIVE_QUESTION_STATS_TABLE"])
    return _dynamodb_table


def _parse_count(value: Any) -> int:
    if isinstance(value, Decimal):
        return max(0, int(value))
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _item_to_record(item: dict[str, Any]) -> dict[str, Any] | None:
    """Convert a DynamoDB item to a normalized analytics record."""
    if item.get("entityType") != ENTITY_TYPE_QUESTION:
        return None

    text = item.get("questionText")
    if not isinstance(text, str) or not text.strip():
        return None

    count = _parse_count(item.get("count", 0))
    if count < 1:
        return None

    question_id = item.get("questionId")
    if not isinstance(question_id, str) or not question_id:
        return None

    return {
        "questionId": question_id,
        "question": text.strip(),
        "count": count,
        "fallbackCount": _parse_count(item.get("fallbackCount", 0)),
        "lastAskedAt": item.get("lastAskedAt", ""),
        "createdAt": item.get("createdAt", ""),
        "updatedAt": item.get("updatedAt", ""),
    }


def _sort_records(records: list[dict[str, Any]], sort_by: str) -> list[dict[str, Any]]:
    if sort_by == SORT_RECENT:
        return sorted(
            records,
            key=lambda row: (row.get("lastAskedAt") or "", row.get("question", "").lower()),
            reverse=True,
        )
    if sort_by == SORT_FALLBACKS:
        return sorted(
            records,
            key=lambda row: (-row["fallbackCount"], -row["count"], row["question"].lower()),
        )
    return sorted(
        records,
        key=lambda row: (-row["count"], row.get("lastAskedAt") or "", row["question"].lower()),
    )


def _scan_all_items(table) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    scan_kwargs: dict[str, Any] = {}
    while True:
        response = table.scan(**scan_kwargs)
        items.extend(response.get("Items", []))
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
        scan_kwargs["ExclusiveStartKey"] = last_key
    return items


def _table_is_empty(table) -> bool:
    response = table.scan(
        FilterExpression="entityType = :entityType",
        ExpressionAttributeValues={":entityType": ENTITY_TYPE_QUESTION},
        Limit=1,
    )
    return len(response.get("Items", [])) == 0


def _put_seed_question(table, question_text: str) -> None:
    normalized = normalize_question_key(question_text)
    if not normalized:
        return

    question_id = _question_id(normalized)
    now = _utc_now_iso()

    try:
        table.put_item(
            Item={
                "questionId": question_id,
                "questionText": question_text,
                "normalizedQuestion": normalized,
                "count": 1,
                "fallbackCount": 0,
                "entityType": ENTITY_TYPE_QUESTION,
                "createdAt": now,
                "updatedAt": now,
                "lastAskedAt": now,
            },
            ConditionExpression="attribute_not_exists(questionId)",
        )
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            return
        raise


def seed_questions_if_empty() -> None:
    """
    Seed the DynamoDB table once with common IT Support questions when empty.
    Skips items that already exist (same questionId).
    """
    global _seed_attempted
    if _seed_attempted:
        return
    _seed_attempted = True

    try:
        table = _get_table()
        if not _table_is_empty(table):
            logger.info("QuestionStats table is not empty; skipping seed data.")
            return

        logger.info("QuestionStats table is empty; seeding %d default questions.", len(SEED_QUESTIONS))
        for question_text in SEED_QUESTIONS:
            _put_seed_question(table, question_text)

    except (ClientError, BotoCoreError) as exc:
        logger.exception("Failed to seed QuestionStats table: %s", exc)
    except Exception as exc:
        logger.exception("Unexpected error seeding QuestionStats table: %s", exc)


def record_question(question: str, *, is_fallback: bool = False) -> None:
    """
    Record a submitted question in DynamoDB.
    Increments count and updates lastAskedAt; increments fallbackCount when the answer was a fallback.
    """
    normalized = normalize_question_key(question)
    if not normalized:
        return

    table = _get_table()
    question_id = _question_id(normalized)
    display = question.strip()
    now = _utc_now_iso()
    fallback_inc = 1 if is_fallback else 0

    try:
        table.update_item(
            Key={"questionId": question_id},
            UpdateExpression=(
                "ADD #count :one, fallbackCount :fallbackInc "
                "SET questionText = if_not_exists(questionText, :text), "
                "normalizedQuestion = :normalized, "
                "entityType = if_not_exists(entityType, :entityType), "
                "updatedAt = :updated, "
                "lastAskedAt = :lastAsked, "
                "createdAt = if_not_exists(createdAt, :created)"
            ),
            ExpressionAttributeNames={"#count": "count"},
            ExpressionAttributeValues={
                ":one": 1,
                ":fallbackInc": fallback_inc,
                ":text": display,
                ":normalized": normalized,
                ":entityType": ENTITY_TYPE_QUESTION,
                ":updated": now,
                ":lastAsked": now,
                ":created": now,
            },
        )
    except (ClientError, BotoCoreError) as exc:
        logger.exception("Failed to record question in DynamoDB: %s", exc)
    except Exception as exc:
        logger.exception("Unexpected error recording question stats: %s", exc)


def get_questions(
    sort_by: str | None = SORT_POPULAR,
    limit: int | None = None,
) -> tuple[list[dict[str, Any]], bool]:
    """
    Return question analytics records, optionally sorted and limited for the sidebar.
    When sort_by is None, records are returned unsorted for client-side portal sorting.
    Returns (records, success). success is False when DynamoDB is unavailable.
    """
    sidebar_sort = sort_by
    if limit is not None and sidebar_sort not in (SORT_POPULAR, SORT_RECENT, SORT_FALLBACKS):
        sidebar_sort = SORT_POPULAR

    try:
        seed_questions_if_empty()
        table = _get_table()
        items = _scan_all_items(table)

        records: list[dict[str, Any]] = []
        for item in items:
            record = _item_to_record(item)
            if record:
                records.append(record)

        if limit is not None:
            sorted_records = _sort_records(records, sidebar_sort)
            sorted_records = sorted_records[:limit]
            return [
                {"question": row["question"], "count": row["count"]}
                for row in sorted_records
            ], True

        return records, True

    except (ClientError, BotoCoreError) as exc:
        logger.exception("Failed to load questions from DynamoDB: %s", exc)
        return [], False
    except Exception as exc:
        logger.exception("Unexpected error loading questions: %s", exc)
        return [], False


def get_top_questions(mode: str = SORT_POPULAR, limit: int = TOP_QUESTIONS_LIMIT) -> list[dict[str, Any]]:
    """
    Return the top sidebar questions for the selected mode.
    popular: count descending. recent: lastAskedAt descending.
    """
    if mode not in (SORT_POPULAR, SORT_RECENT):
        mode = SORT_POPULAR

    questions, success = get_questions(sort_by=mode, limit=limit)
    if not success:
        return []
    return questions


def delete_question(question_id: str) -> bool:
    """
    Delete a single analytics question from DynamoDB.
    Does not affect S3, Bedrock, or the Knowledge Base.
    """
    if not question_id or not isinstance(question_id, str):
        return False

    question_id = question_id.strip()
    if question_id.startswith("SYSTEM#"):
        logger.warning("Refusing to delete internal system record: %s", question_id)
        return False

    try:
        table = _get_table()
        table.delete_item(Key={"questionId": question_id})
        return True
    except (ClientError, BotoCoreError) as exc:
        logger.exception("Failed to delete question %s from DynamoDB: %s", question_id, exc)
        return False
    except Exception as exc:
        logger.exception("Unexpected error deleting question %s: %s", question_id, exc)
        return False


def _coerce_bool(value: Any, default: bool = True) -> bool:
    """Normalize DynamoDB or serialized values into a strict boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, Decimal):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ("true", "1", "yes"):
            return True
        if normalized in ("false", "0", "no"):
            return False
        return default
    if value is None:
        return default
    return bool(value)


def get_kb_sync_status() -> tuple[dict[str, Any], bool]:
    """
    Return the global Knowledge Base synchronization state from the hidden system record.
    Returns (status, success). Defaults to synced when the record does not exist.
    """
    default_status = {
        "isSynced": True,
        "lastSyncRequestedAt": None,
        "updatedAt": None,
    }

    try:
        table = _get_table()
        response = table.get_item(Key={"questionId": KB_SYNC_STATUS_ID})
        item = response.get("Item")
        if not item:
            return default_status, True

        return {
            "isSynced": _coerce_bool(item.get("isSynced"), default=True),
            "lastSyncRequestedAt": item.get("lastSyncRequestedAt"),
            "updatedAt": item.get("updatedAt"),
        }, True
    except (ClientError, BotoCoreError) as exc:
        logger.exception("Failed to load Knowledge Base sync status: %s", exc)
        return default_status, False
    except Exception as exc:
        logger.exception("Unexpected error loading Knowledge Base sync status: %s", exc)
        return default_status, False


def set_kb_sync_pending() -> bool:
    """Mark the Knowledge Base as having pending changes after a CSV update."""
    now = _utc_now_iso()

    try:
        table = _get_table()
        table.update_item(
            Key={"questionId": KB_SYNC_STATUS_ID},
            UpdateExpression=(
                "SET entityType = :entityType, "
                "isSynced = :isSynced, "
                "updatedAt = :updatedAt"
            ),
            ExpressionAttributeValues={
                ":entityType": ENTITY_TYPE_SYSTEM,
                ":isSynced": False,
                ":updatedAt": now,
            },
        )
        return True
    except (ClientError, BotoCoreError) as exc:
        logger.exception("Failed to mark Knowledge Base sync as pending: %s", exc)
        return False
    except Exception as exc:
        logger.exception("Unexpected error marking Knowledge Base sync pending: %s", exc)
        return False


def set_kb_sync_completed() -> bool:
    """Mark the Knowledge Base as synced after a successful Bedrock ingestion request."""
    now = _utc_now_iso()

    try:
        table = _get_table()
        table.update_item(
            Key={"questionId": KB_SYNC_STATUS_ID},
            UpdateExpression=(
                "SET entityType = :entityType, "
                "isSynced = :isSynced, "
                "lastSyncRequestedAt = :lastSyncRequestedAt, "
                "updatedAt = :updatedAt"
            ),
            ExpressionAttributeValues={
                ":entityType": ENTITY_TYPE_SYSTEM,
                ":isSynced": True,
                ":lastSyncRequestedAt": now,
                ":updatedAt": now,
            },
        )
        return True
    except (ClientError, BotoCoreError) as exc:
        logger.exception("Failed to mark Knowledge Base sync as completed: %s", exc)
        return False
    except Exception as exc:
        logger.exception("Unexpected error marking Knowledge Base sync completed: %s", exc)
        return False
