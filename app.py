"""
Smart Employee Assistant — Flask application for IT Support Q&A via Amazon Bedrock Knowledge Base.
"""

from dotenv import load_dotenv

# Load .env before any other application code reads environment variables or creates AWS clients.
load_dotenv()

import logging
import os
import re
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from flask import Flask, jsonify, render_template, request

from question_stats import get_top_questions, record_successful_question

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

MAX_QUESTION_LENGTH = 500

AUTH_SOURCE = "environment variables (.env)"

REQUIRED_ENV_VARS = (
    "AWS_REGION",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "BEDROCK_KNOWLEDGE_BASE_ID",
    "BEDROCK_MODEL_ARN",
)

USER_ERROR_MESSAGE = (
    "We could not process your request at this time. "
    "Please try again later or contact the IT Service Desk."
)
KB_NOT_FOUND_MESSAGE = (
    "I could not find a matching answer in the IT knowledge base. "
    "Please contact the IT Service Desk at https://amdocs.service-now.com "
    "or call +1-800-555-0199."
)

# Prompt must include $search_results$ and $output_format_instructions$ for citation parsing.
GROUNDED_PROMPT_TEMPLATE = f"""You are the Smart Employee Assistant for Amdocs internal IT Support.

Answer the employee question using ONLY the search results below from the IT knowledge base.

Rules:
- Use only information explicitly stated in the search results.
- Do not use general knowledge, assumptions, or information outside the search results.
- Do not guess, infer, or invent links, phone numbers, tools, ticket categories, or procedures.
- If the search results do not contain enough information to answer the question, respond with this message exactly and nothing else:
{KB_NOT_FOUND_MESSAGE}

Employee question:
$query$

Search results:
$search_results$

$output_format_instructions$
"""

_NO_KB_MATCH_PHRASES = (
    "could not find",
    "couldn't find",
    "unable to find",
    "do not contain information",
    "does not contain information",
    "doesn't contain information",
    "no exact answer",
    "not found in the",
    "cannot answer",
    "can't answer",
    "unable to assist",
    "unable to help",
)


def validate_required_env() -> dict[str, str]:
    """
    Validate that all required AWS and Bedrock variables are set in the environment.
    Credentials must come from .env / process environment only (not ~/.aws/credentials).
    """
    missing: list[str] = []
    config: dict[str, str] = {}

    for name in REQUIRED_ENV_VARS:
        value = os.getenv(name, "").strip()
        if not value:
            missing.append(name)
        else:
            config[name] = value

    if missing:
        message = (
            "Startup failed: missing required environment variables: "
            f"{', '.join(missing)}. "
            "Define them in .env (see .env.example). "
            "This application does not use ~/.aws/credentials or AWS CLI profiles."
        )
        logger.error(message)
        raise SystemExit(message)

    return config


def log_aws_configuration(config: dict[str, str]) -> None:
    """Log non-secret AWS configuration details at startup."""
    logger.info("AWS region: %s", config["AWS_REGION"])
    logger.info("Bedrock Knowledge Base ID: %s", config["BEDROCK_KNOWLEDGE_BASE_ID"])
    logger.info("AWS authentication source: %s", AUTH_SOURCE)


AWS_CONFIG = validate_required_env()
log_aws_configuration(AWS_CONFIG)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "change-me-in-production")

_bedrock_client = None


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name, str(default)).strip().lower()
    return value in ("1", "true", "yes", "on")


def get_bedrock_client():
    """
    Create a Bedrock Agent Runtime client using credentials from environment variables only.
    load_dotenv() runs at module import time before this client is first created.
    """
    global _bedrock_client
    if _bedrock_client is not None:
        return _bedrock_client

    _bedrock_client = boto3.client(
        "bedrock-agent-runtime",
        region_name=AWS_CONFIG["AWS_REGION"],
        aws_access_key_id=AWS_CONFIG["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=AWS_CONFIG["AWS_SECRET_ACCESS_KEY"],
    )
    return _bedrock_client


def validate_question(raw: str | None) -> tuple[str | None, str | None]:
    """Validate and normalize user question. Returns (question, error_message)."""
    if raw is None:
        return None, "Please enter a question."

    question = raw.strip()
    if not question:
        return None, "Please enter a question."
    if len(question) > MAX_QUESTION_LENGTH:
        return None, f"Question must be {MAX_QUESTION_LENGTH} characters or fewer."
    return question, None


def extract_answer(response: dict[str, Any]) -> str | None:
    """Safely extract generated text from Bedrock retrieve_and_generate response."""
    try:
        text = response.get("output", {}).get("text")
        if text and isinstance(text, str) and text.strip():
            return text.strip()
    except (AttributeError, TypeError) as exc:
        logger.warning("Unexpected Bedrock response shape: %s", exc)
    return None


def _has_retrieved_references(response: dict[str, Any]) -> bool:
    """Return True when Bedrock returned at least one non-empty retrieved reference."""
    citations = response.get("citations")
    if not citations or not isinstance(citations, list):
        return False

    for citation in citations:
        if not isinstance(citation, dict):
            continue
        references = citation.get("retrievedReferences")
        if references and isinstance(references, list) and len(references) > 0:
            return True
    return False


def _indicates_no_kb_match(answer: str) -> bool:
    """Detect model responses that decline to answer from retrieved context."""
    normalized = answer.strip().lower()
    if normalized == KB_NOT_FOUND_MESSAGE.lower():
        return True
    return any(phrase in normalized for phrase in _NO_KB_MATCH_PHRASES)


def query_knowledge_base(question: str) -> str:
    """
    Query Amazon Bedrock Knowledge Base via retrieve_and_generate.

    Answers are strictly grounded in retrieved Knowledge Base content. Returns a fixed
    fallback message when retrieval citations are missing or the model cannot answer
    from the provided context.
    """
    client = get_bedrock_client()

    try:
        response = client.retrieve_and_generate(
            input={"text": question},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": AWS_CONFIG["BEDROCK_KNOWLEDGE_BASE_ID"],
                    "modelArn": AWS_CONFIG["BEDROCK_MODEL_ARN"],
                    "retrievalConfiguration": {
                        "vectorSearchConfiguration": {
                            "numberOfResults": 5,
                        },
                    },
                    "generationConfiguration": {
                        "inferenceConfig": {
                            "textInferenceConfig": {
                                "temperature": 0.0,
                                "topP": 1.0,
                                "maxTokens": 1024,
                            },
                        },
                        "promptTemplate": {
                            "textPromptTemplate": GROUNDED_PROMPT_TEMPLATE,
                        },
                    },
                },
            },
        )
    except (ClientError, BotoCoreError) as exc:
        logger.exception("Bedrock retrieve_and_generate failed: %s", exc)
        raise

    if not _has_retrieved_references(response):
        logger.info(
            "No citations or retrieved references in Bedrock response; returning KB fallback."
        )
        return KB_NOT_FOUND_MESSAGE

    answer = extract_answer(response)
    if not answer:
        logger.warning("Bedrock returned empty output text despite retrieved references.")
        return KB_NOT_FOUND_MESSAGE

    if _indicates_no_kb_match(answer):
        logger.info("Model indicated no KB match; returning standard fallback message.")
        return KB_NOT_FOUND_MESSAGE

    return answer


def generate_mock_answer(question: str) -> str:
    """Return a professional mock answer for local and Docker testing without Bedrock."""
    q = question.lower()

    if re.search(r"\bvpn\b|remote access|globalprotect", q):
        return (
            "To request VPN access, sign in to ServiceNow at https://amdocs.service-now.com "
            "and open IT Services > Network Access > VPN Request. Select your region "
            "(EMEA, Americas, or APAC), provide your Employee ID (ADM-XXXXX), business "
            "justification, and expected duration. Manager approval is required. After "
            "approval, install the GlobalProtect client from the Company Portal or the "
            "internal software catalog at https://software.amdocs.internal. Configure the "
            "regional portal (for example, vpn-amer.amdocs.com for Americas) and authenticate "
            "with Okta Verify."
        )

    if re.search(r"password|reset|locked account|forgot", q):
        return (
            "Reset your corporate password at https://password.amdocs.internal using "
            "Forgot Password and your Amdocs email plus Employee ID. Complete Okta "
            "verification, then set a password that meets policy (minimum 14 characters with "
            "uppercase, lowercase, number, and special character). If self-service fails or "
            "your account is locked, contact the IT Service Desk at extension 4357 or submit "
            "Account Management > Password Reset – Assisted in ServiceNow."
        )

    if re.search(r"production|prod access|par\b|cyberark|jump host", q):
        return (
            "Complete PROD-101, SEC-205, and CHG-110 in the Amdocs Learning Portal, then "
            "submit a Production Access Request in ServiceNow under IT Services > Access "
            "Management > Production Access Request. Include the target system, access level "
            "(Read-Only, Read-Write, or Admin), and justification linked to a Jira or change "
            "ticket. Access is provisioned through CyberArk via jump-prod.amdocs.internal and "
            "expires after 90 days unless renewed."
        )

    if re.search(r"software|install|license|catalog|company portal|self service", q):
        return (
            "Approved software is available through https://software.amdocs.internal and the "
            "Amdocs Self Service app (macOS) or Company Portal (Windows). For applications not "
            "in the catalog, submit IT Services > Software > Software Installation Request in "
            "ServiceNow with application name, version, vendor, and business justification. "
            "Software Asset Management verifies licensing; new applications may require a "
            "security review of 3–5 business days."
        )

    if re.search(r"mfa|okta|multi.factor|authenticator", q):
        return (
            "Enroll in MFA using the link from okta-admin@amdocs.com within 72 hours of "
            "account creation. Install Okta Verify, sign in at https://amdocs.okta.com, and "
            "scan the QR code. Register at least one backup factor (secondary device, YubiKey "
            "via ServiceNow Account Management > MFA Hardware Token, or security questions). "
            "MFA is required for VPN, email, ServiceNow, and GitLab."
        )

    if re.search(r"laptop|hardware|replacement|new device", q):
        return (
            "Request a new laptop via ServiceNow under IT Services > Hardware > New Laptop "
            "Request. Hardware tier is assigned by role in Workday (Tier 1 standard, Tier 2 "
            "developer, Tier 3 power user). Standard delivery is 5–7 business days for office "
            "pickup. For repairs, use Hardware > Laptop Repair/Replacement and include your "
            "asset tag (ADM-IT-XXXXXX)."
        )

    if re.search(r"servicenow|incident|ticket|service desk", q):
        return (
            "Create IT incidents at https://amdocs.service-now.com via Create Incident with a "
            "specific category, reproduction steps, Employee ID, asset tag, and business "
            "impact. P1 (Unable to Work) targets 4-hour response; use live chat or call "
            "extension 4357 for urgent issues. Use the Service Catalog for access and "
            "hardware requests, not incidents."
        )

    return (
        "I could not match your question to a specific IT procedure in the current context. "
        "Please include more detail (for example: VPN, password reset, production access, "
        "software installation, MFA, hardware, or ServiceNow). "
        "For immediate assistance, open ServiceNow at https://amdocs.service-now.com "
        "or contact the IT Service Desk at servicedesk@amdocs.com (extension 4357)."
    )


def is_fallback_answer(answer: str) -> bool:
    """Return True when the answer is the standard knowledge-base not-found message."""
    return answer.strip() == KB_NOT_FOUND_MESSAGE


def get_answer(question: str) -> str:
    """Resolve an answer using mock mode or Amazon Bedrock Knowledge Base."""
    if _env_bool("USE_MOCK_ANSWER", default=False):
        logger.info("Returning mock answer (USE_MOCK_ANSWER=true).")
        return generate_mock_answer(question)
    return query_knowledge_base(question)


@app.route("/", methods=["GET"])
def index():
    """Render the home page."""
    return render_template("index.html")


@app.route("/api/common-questions", methods=["GET"])
def common_questions():
    """Return the top successful questions ranked by popularity."""
    try:
        questions = get_top_questions()
        return jsonify({"success": True, "questions": questions})
    except Exception as exc:
        logger.exception("Failed to load common questions: %s", exc)
        return jsonify({"success": True, "questions": []})


@app.route("/ask", methods=["POST"])
def ask():
    """Accept a question and return a JSON answer from the Knowledge Base."""
    payload = request.get_json(silent=True) or {}
    raw_question = payload.get("question")
    if raw_question is None:
        raw_question = request.form.get("question")

    question, validation_error = validate_question(raw_question)
    if validation_error:
        return jsonify({"success": False, "error": validation_error}), 400

    try:
        answer = get_answer(question)
        common = get_top_questions()
        if not is_fallback_answer(answer):
            try:
                record_successful_question(question)
                common = get_top_questions()
            except Exception as exc:
                logger.exception("Failed to record question stats: %s", exc)

        return jsonify({
            "success": True,
            "answer": answer,
            "question": question,
            "common_questions": common,
        })
    except ClientError as exc:
        logger.exception("AWS Bedrock client error: %s", exc.response.get("Error", {}).get("Code"))
        return jsonify({"success": False, "error": USER_ERROR_MESSAGE}), 502
    except BotoCoreError as exc:
        logger.exception("AWS SDK error: %s", exc)
        return jsonify({"success": False, "error": USER_ERROR_MESSAGE}), 502
    except ValueError as exc:
        logger.error("Configuration error: %s", exc)
        return jsonify({"success": False, "error": USER_ERROR_MESSAGE}), 503
    except Exception as exc:
        logger.exception("Unexpected error processing question: %s", exc)
        return jsonify({"success": False, "error": USER_ERROR_MESSAGE}), 500


if __name__ == "__main__":
    debug = os.getenv("FLASK_ENV", "production").lower() == "development"
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=debug)
