"""
Smart Employee Assistant — Flask application for IT Support Q&A via Amazon Bedrock Knowledge Base.
"""

from dotenv import load_dotenv

# Load .env before any other application code reads environment variables or creates AWS clients.
load_dotenv()

import logging
import os
import re
import uuid
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from aws_config import log_upload_account_configuration, validate_upload_account_config
from knowledge_base_service import (
    add_entry as kb_add_entry,
    delete_entry as kb_delete_entry,
    list_entries as kb_list_entries,
    sync_knowledge_base as kb_sync_knowledge_base,
    update_entry as kb_update_entry,
)
from question_stats import (
    SORT_POPULAR,
    SORT_RECENT,
    delete_question,
    get_kb_sync_status,
    get_questions,
    get_top_questions,
    record_question,
    seed_questions_if_empty,
    set_kb_sync_completed,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

MAX_QUESTION_LENGTH = 500

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


AWS_CONFIG = validate_upload_account_config()
log_upload_account_configuration(AWS_CONFIG)
seed_questions_if_empty()

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
        region_name=AWS_CONFIG["ACTIVE_AWS_REGION"],
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
                    "knowledgeBaseId": AWS_CONFIG["ACTIVE_KNOWLEDGE_BASE_ID"],
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


def _parse_agent_completion(completion: Any) -> str:
    """Extract plain text from the Bedrock Agent streaming completion payload."""
    if completion is None:
        return ""

    parts: list[str] = []
    try:
        for event in completion:
            if not isinstance(event, dict):
                continue
            chunk = event.get("chunk")
            if not chunk:
                continue
            payload = chunk.get("bytes")
            if payload:
                parts.append(payload.decode("utf-8"))
    except (TypeError, AttributeError, UnicodeDecodeError) as exc:
        logger.warning("Unexpected Bedrock Agent completion event shape: %s", exc)
        return ""

    return "".join(parts).strip()


def query_bedrock_agent(question: str) -> str:
    """
    Route the employee question through the configured Bedrock Agent.

    The agent selects Knowledge Base retrieval, Action Group tools, or fallback behavior.
    """
    client = get_bedrock_client()
    agent_id = AWS_CONFIG["BEDROCK_AGENT_ID"]
    agent_alias_id = AWS_CONFIG["BEDROCK_AGENT_ALIAS_ID"]
    session_id = str(uuid.uuid4())

    logger.info(
        "Invoking Bedrock Agent: agentId=%s, agentAliasId=%s, sessionId=%s",
        agent_id,
        agent_alias_id,
        session_id,
    )

    try:
        response = client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=question,
        )
    except (ClientError, BotoCoreError) as exc:
        logger.exception("Bedrock Agent invoke_agent failed: %s", exc)
        raise

    answer = _parse_agent_completion(response.get("completion"))
    if not answer:
        logger.warning("Bedrock Agent returned an empty answer.")
        return KB_NOT_FOUND_MESSAGE

    if _indicates_no_kb_match(answer):
        logger.info(
            "Bedrock Agent response indicates no verified match; returning standard fallback."
        )
        return KB_NOT_FOUND_MESSAGE

    logger.info("Bedrock Agent completed successfully (%d characters).", len(answer))
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


def _it_portal_url() -> str:
    """Return the IT Portal or login URL based on session state."""
    if session.get("it_portal_authenticated"):
        return url_for("it_portal")
    return url_for("it_login")


def _is_it_portal_authenticated() -> bool:
    return bool(session.get("it_portal_authenticated"))


def require_it_portal(view: Callable) -> Callable:
    """Require an authenticated IT Portal session for API routes."""

    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any):
        if not _is_it_portal_authenticated():
            return jsonify({
                "success": False,
                "error": "Your IT Portal session has expired. Please sign in again.",
            }), 401
        return view(*args, **kwargs)

    return wrapped


def _verify_it_portal_password(password: str) -> bool:
    expected = os.getenv("IT_PORTAL_PASSWORD", "").strip()
    if not expected:
        logger.warning("IT_PORTAL_PASSWORD is not configured; IT Portal login is disabled.")
        return False
    return password == expected


def _normalize_sidebar_sort(raw: str | None) -> str:
    if raw == SORT_RECENT:
        return SORT_RECENT
    return SORT_POPULAR


def format_display_timestamp(iso_value: str | None) -> str:
    """Format an ISO timestamp for display in the IT Portal."""
    if not iso_value:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except (ValueError, TypeError):
        return str(iso_value)


def _enrich_portal_questions(questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for row in questions:
        enriched.append({
            **row,
            "lastAskedAtDisplay": format_display_timestamp(row.get("lastAskedAt")),
            "createdAtDisplay": format_display_timestamp(row.get("createdAt")),
        })
    return enriched


def _coerce_sync_bool(value: Any, default: bool = True) -> bool:
    """Normalize sync status booleans from DynamoDB or request payloads."""
    if isinstance(value, bool):
        return value
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


def _format_sync_status_payload(status_data: dict[str, Any] | None) -> dict[str, Any]:
    status_data = status_data or {}
    last_sync = status_data.get("lastSyncRequestedAt")
    return {
        "isSynced": _coerce_sync_bool(status_data.get("isSynced"), default=True),
        "lastSyncRequestedAt": last_sync,
        "lastSyncRequestedDisplay": (
            format_display_timestamp(last_sync) if last_sync else "Not available"
        ),
    }


def _sync_status_api_payload(sync_status: dict[str, Any], **extra: Any) -> dict[str, Any]:
    """Return sync status fields at the top level and in syncStatus."""
    payload = {
        "isSynced": sync_status["isSynced"],
        "lastSyncRequestedAt": sync_status["lastSyncRequestedAt"],
        "lastSyncRequestedDisplay": sync_status["lastSyncRequestedDisplay"],
        "syncStatus": sync_status,
    }
    payload.update(extra)
    return payload


def _load_sync_status_response() -> tuple[dict[str, Any], bool]:
    status_data, success = get_kb_sync_status()
    return _format_sync_status_payload(status_data), success


def get_answer(question: str) -> str:
    """Resolve an answer using mock mode or the configured Bedrock Agent."""
    if _env_bool("USE_MOCK_ANSWER", default=False):
        logger.info("Answer path: mock mode (USE_MOCK_ANSWER=true).")
        return generate_mock_answer(question)

    logger.info("Answer path: Bedrock Agent (invoke_agent).")
    try:
        return query_bedrock_agent(question)
    except (ClientError, BotoCoreError):
        logger.warning(
            "Bedrock Agent unavailable; falling back to direct Knowledge Base retrieval."
        )
        return query_knowledge_base(question)


def _wants_json_response() -> bool:
    """Return True when the client expects a JSON error payload instead of HTML."""
    if request.path.startswith("/it-portal/api/") or request.path.startswith("/api/"):
        return True
    if request.path == "/ask":
        return True
    accept = request.accept_mimetypes
    return (
        accept.best_match(["application/json", "text/html"]) == "application/json"
        and accept["application/json"] > accept["text/html"]
    )


def _json_or_error_page(status_code: int, message: str, title: str):
    """Return a styled HTML error page or JSON error payload based on the request."""
    if _wants_json_response():
        return jsonify({"success": False, "error": message}), status_code

    return render_template(
        "error.html",
        status_code=status_code,
        title=title,
        message=message,
        home_url=url_for("index"),
        it_portal_url=_it_portal_url(),
    ), status_code


@app.errorhandler(404)
def handle_not_found(error):
    """Render a styled not-found page or JSON error for API clients."""
    return _json_or_error_page(
        404,
        "The requested resource was not found.",
        "Page not found",
    )


@app.errorhandler(405)
def handle_method_not_allowed(error):
    """Render a styled method-not-allowed page or JSON error for API clients."""
    return _json_or_error_page(
        405,
        "This request method is not supported.",
        "Method not allowed",
    )


@app.errorhandler(403)
def handle_forbidden(error):
    """Render a styled access-denied page or JSON error for API clients."""
    return _json_or_error_page(
        403,
        "You do not have permission to access this resource.",
        "Access denied",
    )


@app.errorhandler(500)
def handle_internal_error(error):
    """Render a styled server error page or JSON error for API clients."""
    logger.exception("Unhandled server error: %s", error)
    return _json_or_error_page(
        500,
        USER_ERROR_MESSAGE,
        "Something went wrong",
    )


@app.route("/", methods=["GET"])
def index():
    """Render the home page."""
    return render_template("index.html", it_portal_url=_it_portal_url())


@app.route("/api/common-questions", methods=["GET"])
def common_questions():
    """Return the top sidebar questions for the selected sort mode."""
    sort_mode = _normalize_sidebar_sort(request.args.get("sort"))
    try:
        questions = get_top_questions(mode=sort_mode)
        return jsonify({"success": True, "questions": questions, "sort": sort_mode})
    except Exception as exc:
        logger.exception("Failed to load common questions: %s", exc)
        return jsonify({"success": True, "questions": [], "sort": sort_mode})


@app.route("/it-login", methods=["GET", "POST"])
def it_login():
    """Password-based IT Portal sign-in."""
    if _is_it_portal_authenticated():
        return redirect(url_for("it_portal"))

    error_message = None
    if request.method == "POST":
        password = request.form.get("password", "")
        if _verify_it_portal_password(password):
            session["it_portal_authenticated"] = True
            return redirect(url_for("it_portal"))
        error_message = "Invalid password. Please try again."

    return render_template(
        "it_login.html",
        error_message=error_message,
        home_url=url_for("index"),
    )


@app.route("/it-logout", methods=["POST"])
def it_logout():
    """Clear IT Portal session and return to login."""
    session.pop("it_portal_authenticated", None)
    return redirect(url_for("it_login"))


@app.route("/it-portal", methods=["GET"])
def it_portal():
    """IT Portal workspace for analytics and Knowledge Base management."""
    if not _is_it_portal_authenticated():
        return redirect(url_for("it_login"))

    questions, success = get_questions(sort_by=None)
    error_message = None if success else "Unable to load question analytics at this time. Please try again later."
    initial_sync_status, _sync_ok = _load_sync_status_response()

    return render_template(
        "it_portal.html",
        questions=_enrich_portal_questions(questions),
        analytics_error=error_message,
        initial_sync_status=initial_sync_status,
        home_url=url_for("index"),
        logout_url=url_for("it_logout"),
        analytics_delete_url_template=url_for("it_portal_delete_analytics", question_id="__ID__"),
        knowledge_list_url=url_for("it_portal_list_knowledge"),
        knowledge_sync_url=url_for("it_portal_sync_knowledge"),
        knowledge_sync_status_url=url_for("it_portal_sync_status"),
        knowledge_update_url_template=url_for("it_portal_update_knowledge", entry_id="__ID__"),
        knowledge_delete_url_template=url_for("it_portal_delete_knowledge", entry_id="__ID__"),
    )


@app.route("/it-portal/api/analytics/<question_id>", methods=["DELETE"])
@require_it_portal
def it_portal_delete_analytics(question_id: str):
    """Delete a single analytics record from DynamoDB (does not affect the Knowledge Base)."""
    if not delete_question(question_id):
        logger.error("IT Portal analytics delete failed for questionId=%s", question_id)
        return jsonify({"success": False, "error": "Unable to delete record."}), 500

    return jsonify({
        "success": True,
        "message": "Analytics record deleted successfully.",
    })


@app.route("/it-portal/api/knowledge", methods=["GET"])
@require_it_portal
def it_portal_list_knowledge():
    """Return all Knowledge Base entries from the S3 CSV source."""
    result = kb_list_entries()
    if not result.success:
        return jsonify({"success": False, "error": result.error or "Unable to load Knowledge Base entries."}), 500

    sync_status, sync_ok = _load_sync_status_response()
    if not sync_ok:
        return jsonify({"success": False, "error": "Unable to load synchronization status."}), 500

    return jsonify({
        "success": True,
        "entries": result.data,
        "syncStatus": sync_status,
    })


@app.route("/it-portal/api/knowledge/sync-status", methods=["GET"])
@require_it_portal
def it_portal_sync_status():
    """Return the current Knowledge Base synchronization state."""
    sync_status, sync_ok = _load_sync_status_response()
    if not sync_ok:
        return jsonify({"success": False, "error": "Unable to load synchronization status."}), 500

    return jsonify(_sync_status_api_payload(sync_status, success=True))


@app.route("/it-portal/api/knowledge/sync", methods=["POST"])
@require_it_portal
def it_portal_sync_knowledge():
    """Manually trigger Bedrock Knowledge Base synchronization."""
    sync_result = kb_sync_knowledge_base()
    if not sync_result.success:
        return jsonify({
            "success": False,
            "error": sync_result.error or "Synchronization failed.",
        }), 500

    if not set_kb_sync_completed():
        logger.error("Bedrock sync started but failed to update Knowledge Base sync status.")
        return jsonify({
            "success": False,
            "error": "Synchronization started but status could not be updated.",
        }), 500

    sync_status, _sync_ok = _load_sync_status_response()
    return jsonify(_sync_status_api_payload(
        sync_status,
        success=True,
        message="Knowledge Base synchronization started successfully.",
    ))


@app.route("/it-portal/api/knowledge", methods=["POST"])
@require_it_portal
def it_portal_create_knowledge():
    """Create a Knowledge Base entry and mark pending synchronization."""
    payload = request.get_json(silent=True) or {}
    result = kb_add_entry(
        question=str(payload.get("question", "")),
        answer=str(payload.get("answer", "")),
        category=str(payload.get("category", "")),
        keywords=str(payload.get("keywords", "")),
    )

    if not result.success:
        status = 409 if result.error and "already exists" in result.error.lower() else 400
        return jsonify({"success": False, "error": result.error or "Unable to create knowledge entry."}), status

    status_result, status_ok = _load_sync_status_response()
    sync_payload = status_result if status_ok else {"isSynced": False}

    return jsonify({
        "success": True,
        "message": result.message,
        "entry": result.data,
        "syncStatus": sync_payload,
    })


@app.route("/it-portal/api/knowledge/<entry_id>", methods=["PUT"])
@require_it_portal
def it_portal_update_knowledge(entry_id: str):
    """Update a Knowledge Base entry and mark pending synchronization."""
    payload = request.get_json(silent=True) or {}
    result = kb_update_entry(
        entry_id=entry_id,
        question=str(payload.get("question", "")),
        answer=str(payload.get("answer", "")),
        category=str(payload.get("category", "")),
        keywords=str(payload.get("keywords", "")),
    )

    if not result.success:
        status = 404 if result.error and "not found" in result.error.lower() else 400
        if result.error and "already exists" in result.error.lower():
            status = 409
        return jsonify({"success": False, "error": result.error or "Unable to update knowledge entry."}), status

    status_result, status_ok = _load_sync_status_response()
    sync_payload = status_result if status_ok else {"isSynced": False}

    return jsonify({
        "success": True,
        "message": result.message,
        "entry": result.data,
        "syncStatus": sync_payload,
    })


@app.route("/it-portal/api/knowledge/<entry_id>", methods=["DELETE"])
@require_it_portal
def it_portal_delete_knowledge(entry_id: str):
    """Delete a Knowledge Base entry and mark pending synchronization."""
    result = kb_delete_entry(entry_id)

    if not result.success:
        status = 404 if result.error and "not found" in result.error.lower() else 500
        return jsonify({"success": False, "error": result.error or "Unable to delete knowledge entry."}), status

    status_result, status_ok = _load_sync_status_response()
    sync_payload = status_result if status_ok else {"isSynced": False}

    return jsonify({
        "success": True,
        "message": result.message,
        "syncStatus": sync_payload,
    })


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
        record_question(question, is_fallback=is_fallback_answer(answer))
        sort_mode = _normalize_sidebar_sort(payload.get("sort"))
        common = get_top_questions(mode=sort_mode)

        return jsonify({
            "success": True,
            "answer": answer,
            "question": question,
            "common_questions": common,
            "sort": sort_mode,
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
