"""
Active AWS configuration for the uploadAccount environment profile.

Legacy variables (AWS_REGION, BEDROCK_KNOWLEDGE_BASE_ID, etc.) may remain in .env
for reference but are not used when uploadAccount values are configured.
"""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

REQUIRED_UPLOAD_ACCOUNT_VARS = (
    "AWS_REGION_uploadAccount",
    "Knowledge_Base_ID_uploadAccount",
    "Data_Source_ID_uploadAccount",
    "Bucket_Name_uploadAccount",
    "IAM_Role_ARN_uploadAccount",
    "QUESTION_STATS_TABLE",
)

REQUIRED_CREDENTIAL_VARS = (
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "BEDROCK_MODEL_ARN",
)

_UPLOAD_CONFIG: dict[str, str] | None = None


def validate_upload_account_config() -> dict[str, Any]:
    """
    Validate uploadAccount and credential environment variables at startup.
    Returns the active configuration map used by Bedrock, S3, and DynamoDB clients.
    """
    missing: list[str] = []
    raw: dict[str, str] = {}

    for name in REQUIRED_UPLOAD_ACCOUNT_VARS + REQUIRED_CREDENTIAL_VARS:
        value = os.getenv(name, "").strip()
        if not value:
            missing.append(name)
        else:
            raw[name] = value

    if missing:
        message = (
            "Startup failed: missing required environment variables: "
            f"{', '.join(missing)}. "
            "Define uploadAccount settings and credentials in .env (see .env.example)."
        )
        logger.error(message)
        raise SystemExit(message)

    config: dict[str, Any] = {
        **raw,
        "ACTIVE_AWS_REGION": raw["AWS_REGION_uploadAccount"],
        "ACTIVE_KNOWLEDGE_BASE_ID": raw["Knowledge_Base_ID_uploadAccount"],
        "ACTIVE_DATA_SOURCE_ID": raw["Data_Source_ID_uploadAccount"],
        "ACTIVE_BUCKET_NAME": raw["Bucket_Name_uploadAccount"],
        "ACTIVE_IAM_ROLE_ARN": raw["IAM_Role_ARN_uploadAccount"],
        "ACTIVE_QUESTION_STATS_TABLE": raw["QUESTION_STATS_TABLE"],
    }

    global _UPLOAD_CONFIG
    _UPLOAD_CONFIG = config
    return config


def get_upload_account_config() -> dict[str, Any]:
    """Return validated uploadAccount configuration (loads once at startup)."""
    global _UPLOAD_CONFIG
    if _UPLOAD_CONFIG is None:
        _UPLOAD_CONFIG = validate_upload_account_config()
    return _UPLOAD_CONFIG


def log_upload_account_configuration(config: dict[str, Any]) -> None:
    """Log non-secret active AWS configuration at startup."""
    logger.info("Active AWS region (uploadAccount): %s", config["ACTIVE_AWS_REGION"])
    logger.info("Active Knowledge Base ID (uploadAccount): %s", config["ACTIVE_KNOWLEDGE_BASE_ID"])
    logger.info("Active Data Source ID (uploadAccount): %s", config["ACTIVE_DATA_SOURCE_ID"])
    logger.info("Active S3 bucket (uploadAccount): %s", config["ACTIVE_BUCKET_NAME"])
    logger.info("Active DynamoDB table: %s", config["ACTIVE_QUESTION_STATS_TABLE"])
    logger.info("AWS authentication source: environment variables (.env)")
