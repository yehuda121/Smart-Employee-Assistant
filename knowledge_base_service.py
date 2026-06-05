"""
Knowledge Base management service for the IT Portal.

Handles CSV source files stored in S3 and triggers Bedrock Knowledge Base ingestion jobs.
Analytics data remains in DynamoDB (question_stats.py) and is not modified here.
"""

from __future__ import annotations

import csv
import io
import logging
import os
import re
from dataclasses import dataclass
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from aws_config import get_upload_account_config
from question_stats import normalize_question_key, set_kb_sync_pending

logger = logging.getLogger(__name__)

CSV_FIELDNAMES = ("id", "category", "question", "answer", "keywords", "source_document")
DEFAULT_CSV_S3_KEY = "it_support_faq_dataset.csv"
MAX_QUESTION_LENGTH = 500
MAX_ANSWER_LENGTH = 8000
MAX_CATEGORY_LENGTH = 120
MAX_KEYWORDS_LENGTH = 500

_s3_client = None
_bedrock_agent_client = None


@dataclass
class ServiceResult:
    """Standard result object for Knowledge Base service operations."""

    success: bool
    message: str = ""
    data: Any = None
    error: str | None = None


def _get_csv_s3_key() -> str:
    key = os.getenv("KNOWLEDGE_BASE_CSV_S3_KEY", DEFAULT_CSV_S3_KEY).strip()
    return key or DEFAULT_CSV_S3_KEY


def _get_credentials() -> tuple[str, str, str, str]:
    config = get_upload_account_config()
    return (
        config["ACTIVE_AWS_REGION"],
        config["AWS_ACCESS_KEY_ID"],
        config["AWS_SECRET_ACCESS_KEY"],
        config["ACTIVE_BUCKET_NAME"],
    )


def _get_s3_client():
    global _s3_client
    if _s3_client is not None:
        return _s3_client

    region, access_key, secret_key, _bucket = _get_credentials()
    _s3_client = boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    return _s3_client


def _get_bedrock_agent_client():
    global _bedrock_agent_client
    if _bedrock_agent_client is not None:
        return _bedrock_agent_client

    region, access_key, secret_key, _bucket = _get_credentials()
    _bedrock_agent_client = boto3.client(
        "bedrock-agent",
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    return _bedrock_agent_client


def _default_source_document(category: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", category.lower()).strip("-")
    return f"{slug or 'general'}.md"


def _next_entry_id(entries: list[dict[str, str]]) -> str:
    max_num = 0
    for entry in entries:
        match = re.match(r"^IT-(\d+)$", entry.get("id", "").strip(), re.IGNORECASE)
        if match:
            max_num = max(max_num, int(match.group(1)))
    return f"IT-{max_num + 1:03d}"


def _validate_entry_fields(
    question: str,
    answer: str,
    category: str,
    keywords: str,
) -> tuple[dict[str, str] | None, str | None]:
    question = question.strip()
    answer = answer.strip()
    category = category.strip()
    keywords = keywords.strip()

    if not question:
        return None, "Question is required."
    if not answer:
        return None, "Answer is required."
    if not category:
        return None, "Category is required."
    if len(question) > MAX_QUESTION_LENGTH:
        return None, f"Question must be {MAX_QUESTION_LENGTH} characters or fewer."
    if len(answer) > MAX_ANSWER_LENGTH:
        return None, f"Answer must be {MAX_ANSWER_LENGTH} characters or fewer."
    if len(category) > MAX_CATEGORY_LENGTH:
        return None, f"Category must be {MAX_CATEGORY_LENGTH} characters or fewer."
    if len(keywords) > MAX_KEYWORDS_LENGTH:
        return None, f"Keywords must be {MAX_KEYWORDS_LENGTH} characters or fewer."

    return {
        "question": question,
        "answer": answer,
        "category": category,
        "keywords": keywords,
    }, None


def _entry_to_public(entry: dict[str, str]) -> dict[str, str]:
    return {
        "id": entry.get("id", ""),
        "category": entry.get("category", ""),
        "question": entry.get("question", ""),
        "answer": entry.get("answer", ""),
        "keywords": entry.get("keywords", ""),
        "source_document": entry.get("source_document", ""),
    }


def download_csv() -> ServiceResult:
    """Download the Knowledge Base CSV from S3."""
    _, _, _, bucket = _get_credentials()
    key = _get_csv_s3_key()

    try:
        response = _get_s3_client().get_object(Bucket=bucket, Key=key)
        content = response["Body"].read().decode("utf-8-sig")
        return ServiceResult(success=True, data=content)
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        logger.exception("Failed to download Knowledge Base CSV from S3 (%s): %s", key, exc)
        if code in ("NoSuchKey", "404"):
            return ServiceResult(success=False, error="Knowledge Base source file was not found.")
        return ServiceResult(success=False, error="Unable to load Knowledge Base entries.")
    except (BotoCoreError, UnicodeDecodeError) as exc:
        logger.exception("Failed to download Knowledge Base CSV: %s", exc)
        return ServiceResult(success=False, error="Unable to load Knowledge Base entries.")


def parse_csv(csv_content: str) -> list[dict[str, str]]:
    """Parse CSV text into a list of entry dictionaries."""
    reader = csv.DictReader(io.StringIO(csv_content))
    entries: list[dict[str, str]] = []

    for row in reader:
        if not row:
            continue
        entry = {field: (row.get(field) or "").strip() for field in CSV_FIELDNAMES}
        if entry["id"] and entry["question"]:
            entries.append(entry)

    return entries


def entries_to_csv(entries: list[dict[str, str]]) -> str:
    """Serialize entries to CSV text."""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_FIELDNAMES, lineterminator="\n")
    writer.writeheader()
    for entry in entries:
        writer.writerow({field: entry.get(field, "") for field in CSV_FIELDNAMES})
    return buffer.getvalue()


def upload_csv(csv_content: str) -> ServiceResult:
    """Upload updated CSV content to S3."""
    _, _, _, bucket = _get_credentials()
    key = _get_csv_s3_key()

    try:
        _get_s3_client().put_object(
            Bucket=bucket,
            Key=key,
            Body=csv_content.encode("utf-8"),
            ContentType="text/csv",
        )
        return ServiceResult(success=True, message="Knowledge Base source file updated.")
    except (ClientError, BotoCoreError) as exc:
        logger.exception("Failed to upload Knowledge Base CSV to S3: %s", exc)
        return ServiceResult(success=False, error="Unable to update Knowledge Base source file.")


def sync_knowledge_base() -> ServiceResult:
    """
    Trigger a Bedrock Knowledge Base ingestion job for the active data source.
    Returns immediately after the job is started (does not wait for completion).
    """
    config = get_upload_account_config()

    try:
        response = _get_bedrock_agent_client().start_ingestion_job(
            knowledgeBaseId=config["ACTIVE_KNOWLEDGE_BASE_ID"],
            dataSourceId=config["ACTIVE_DATA_SOURCE_ID"],
        )
        job_id = response.get("ingestionJob", {}).get("ingestionJobId", "")
        logger.info("Started Knowledge Base ingestion job: %s", job_id or "unknown")
        return ServiceResult(
            success=True,
            message="Knowledge Base synchronization started.",
            data={"ingestionJobId": job_id},
        )
    except (ClientError, BotoCoreError) as exc:
        logger.exception("Failed to start Knowledge Base ingestion job: %s", exc)
        return ServiceResult(success=False, error="Synchronization failed.")


def list_entries() -> ServiceResult:
    """Load all Knowledge Base entries from S3."""
    download = download_csv()
    if not download.success:
        return download

    try:
        entries = parse_csv(download.data)
        public_entries = [_entry_to_public(entry) for entry in entries]
        return ServiceResult(success=True, data=public_entries)
    except Exception as exc:
        logger.exception("Failed to parse Knowledge Base CSV: %s", exc)
        return ServiceResult(success=False, error="Unable to load Knowledge Base entries.")


def _load_entries_mutable() -> tuple[list[dict[str, str]] | None, ServiceResult | None]:
    download = download_csv()
    if not download.success:
        return None, download

    try:
        return parse_csv(download.data), None
    except Exception as exc:
        logger.exception("Failed to parse Knowledge Base CSV: %s", exc)
        return None, ServiceResult(success=False, error="Unable to load Knowledge Base entries.")


def _save_entries(entries: list[dict[str, str]]) -> ServiceResult:
    """Upload CSV changes to S3 and mark global sync state as pending."""
    upload = upload_csv(entries_to_csv(entries))
    if not upload.success:
        return upload

    if not set_kb_sync_pending():
        logger.error("CSV updated but failed to mark Knowledge Base sync as pending.")
        return ServiceResult(
            success=False,
            error="Changes were saved, but synchronization status could not be updated.",
        )

    return ServiceResult(
        success=True,
        message="Knowledge Base updated successfully.",
    )


def _duplicate_exists(
    entries: list[dict[str, str]],
    normalized_question: str,
    *,
    exclude_id: str | None = None,
) -> bool:
    for entry in entries:
        if exclude_id and entry.get("id") == exclude_id:
            continue
        if normalize_question_key(entry.get("question", "")) == normalized_question:
            return True
    return False


def add_entry(
    question: str,
    answer: str,
    category: str,
    keywords: str = "",
) -> ServiceResult:
    """Append a new entry to the Knowledge Base CSV and mark pending sync."""
    validated, error = _validate_entry_fields(question, answer, category, keywords)
    if error:
        return ServiceResult(success=False, error=error)

    entries, load_error = _load_entries_mutable()
    if load_error:
        return load_error

    normalized = normalize_question_key(validated["question"])
    if _duplicate_exists(entries, normalized):
        return ServiceResult(success=False, error="A knowledge entry with this question already exists.")

    new_entry = {
        "id": _next_entry_id(entries),
        "category": validated["category"],
        "question": validated["question"],
        "answer": validated["answer"],
        "keywords": validated["keywords"],
        "source_document": _default_source_document(validated["category"]),
    }
    entries.append(new_entry)

    save_result = _save_entries(entries)
    if not save_result.success:
        return save_result

    return ServiceResult(
        success=True,
        message="Knowledge entry created successfully.",
        data=_entry_to_public(new_entry),
    )


def update_entry(
    entry_id: str,
    question: str,
    answer: str,
    category: str,
    keywords: str = "",
) -> ServiceResult:
    """Update an existing Knowledge Base entry and mark pending sync."""
    entry_id = entry_id.strip()
    if not entry_id:
        return ServiceResult(success=False, error="Entry ID is required.")

    validated, error = _validate_entry_fields(question, answer, category, keywords)
    if error:
        return ServiceResult(success=False, error=error)

    entries, load_error = _load_entries_mutable()
    if load_error:
        return load_error

    normalized = normalize_question_key(validated["question"])
    if _duplicate_exists(entries, normalized, exclude_id=entry_id):
        return ServiceResult(success=False, error="A knowledge entry with this question already exists.")

    updated_entry: dict[str, str] | None = None
    for entry in entries:
        if entry.get("id") == entry_id:
            entry["question"] = validated["question"]
            entry["answer"] = validated["answer"]
            entry["category"] = validated["category"]
            entry["keywords"] = validated["keywords"]
            if not entry.get("source_document"):
                entry["source_document"] = _default_source_document(validated["category"])
            updated_entry = dict(entry)
            break

    if updated_entry is None:
        return ServiceResult(success=False, error="Knowledge entry was not found.")

    save_result = _save_entries(entries)
    if not save_result.success:
        return save_result

    return ServiceResult(
        success=True,
        message="Knowledge entry updated successfully.",
        data=_entry_to_public(updated_entry),
    )


def delete_entry(entry_id: str) -> ServiceResult:
    """Remove a Knowledge Base entry from the CSV and mark pending sync."""
    entry_id = entry_id.strip()
    if not entry_id:
        return ServiceResult(success=False, error="Entry ID is required.")

    entries, load_error = _load_entries_mutable()
    if load_error:
        return load_error

    original_count = len(entries)
    entries = [entry for entry in entries if entry.get("id") != entry_id]

    if len(entries) == original_count:
        return ServiceResult(success=False, error="Knowledge entry was not found.")

    save_result = _save_entries(entries)
    if not save_result.success:
        return save_result

    return ServiceResult(
        success=True,
        message="Knowledge entry deleted successfully.",
    )
