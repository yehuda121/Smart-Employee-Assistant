"""
Popular question tracking for the Most Common Questions panel using Amazon DynamoDB.
Stores question text, normalized form, and usage counts — no answers or user data.
"""

import hashlib
import logging
import os
import re
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

TOP_QUESTIONS_LIMIT = 10

_dynamodb_table = None


def normalize_question_key(question: str) -> str:
    """Normalize question text: trim, lowercase, collapse whitespace."""
    return re.sub(r"\s+", " ", question.strip().lower())


def _question_id(normalized: str) -> str:
    """Stable partition key from normalized question text."""
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_table():
    """Return the configured DynamoDB table, or None if not configured."""
    global _dynamodb_table
    if _dynamodb_table is not None:
        return _dynamodb_table

    table_name = os.getenv("QUESTION_STATS_TABLE", "").strip()
    if not table_name:
        logger.warning("QUESTION_STATS_TABLE is not set; popular questions are disabled.")
        return None

    region = os.getenv("AWS_REGION", "").strip()
    access_key = os.getenv("AWS_ACCESS_KEY_ID", "").strip()
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "").strip()
    if not region or not access_key or not secret_key:
        logger.warning("AWS credentials incomplete; popular questions are disabled.")
        return None

    dynamodb = boto3.resource(
        "dynamodb",
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    _dynamodb_table = dynamodb.Table(table_name)
    return _dynamodb_table


def _parse_count(value: Any) -> int:
    if isinstance(value, Decimal):
        return max(0, int(value))
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def record_question(question: str) -> None:
    """
    Increment usage count for a submitted question in DynamoDB.
    Creates a new item when the normalized question is seen for the first time.
    """
    normalized = normalize_question_key(question)
    if not normalized:
        return

    table = _get_table()
    if table is None:
        return

    question_id = _question_id(normalized)
    display = question.strip()
    now = _utc_now_iso()

    try:
        table.update_item(
            Key={"questionId": question_id},
            UpdateExpression=(
                "ADD #count :inc "
                "SET questionText = if_not_exists(questionText, :text), "
                "normalizedQuestion = :normalized, "
                "updatedAt = :updated, "
                "createdAt = if_not_exists(createdAt, :created)"
            ),
            ExpressionAttributeNames={"#count": "count"},
            ExpressionAttributeValues={
                ":inc": 1,
                ":text": display,
                ":normalized": normalized,
                ":updated": now,
                ":created": now,
            },
        )
    except (ClientError, BotoCoreError) as exc:
        logger.exception("Failed to record question in DynamoDB: %s", exc)
    except Exception as exc:
        logger.exception("Unexpected error recording question stats: %s", exc)


def get_top_questions(limit: int = TOP_QUESTIONS_LIMIT) -> list[dict[str, Any]]:
    """
    Return the top questions by usage count from DynamoDB.
    Sorted by count descending. Returns an empty list on error or when no data exists.
    """
    table = _get_table()
    if table is None:
        return []

    try:
        items: list[dict[str, Any]] = []
        scan_kwargs: dict[str, Any] = {}

        while True:
            response = table.scan(**scan_kwargs)
            items.extend(response.get("Items", []))
            last_key = response.get("LastEvaluatedKey")
            if not last_key:
                break
            scan_kwargs["ExclusiveStartKey"] = last_key

        ranked: list[dict[str, Any]] = []
        for item in items:
            text = item.get("questionText")
            if not isinstance(text, str) or not text.strip():
                continue
            count = _parse_count(item.get("count", 0))
            if count < 1:
                continue
            ranked.append({"question": text.strip(), "count": count})

        ranked.sort(key=lambda row: (-row["count"], row["question"].lower()))
        return ranked[:limit]

    except (ClientError, BotoCoreError) as exc:
        logger.exception("Failed to load popular questions from DynamoDB: %s", exc)
        return []
    except Exception as exc:
        logger.exception("Unexpected error loading popular questions: %s", exc)
        return []
