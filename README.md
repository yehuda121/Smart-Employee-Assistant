# Smart Employee Assistant

Internal IT Support assistant for employees. The solution combines a **Flask** web application, **Amazon Bedrock Knowledge Base**, **Amazon Bedrock Agent** with **Action Groups**, **AWS Lambda**, **Amazon DynamoDB**, **Amazon S3**, **Docker**, and optional **Amazon EC2** deployment.

Employees ask IT procedure questions through a web UI. Answers must come only from approved sources—Knowledge Base content, registered service-owner records, or validated external IP lookup results—not from general model knowledge.

---

## Overview

Smart Employee Assistant helps employees find approved guidance for VPN access, password reset, production access, software installation, ServiceNow workflows, service ownership, and related IT topics.

The project has two user-facing surfaces:

| Surface | Route | Audience | Purpose |
|---------|-------|----------|---------|
| **Employee assistant** | `/` | Employees | Submit questions and receive grounded answers |
| **IT Portal** | `/it-login`, `/it-portal` | IT Operations | Analytics dashboard and Knowledge Base management |

Behind the UI, Amazon Bedrock orchestrates answering through a Knowledge Base (S3-backed FAQ and procedure documents), Action Group tools backed by Lambda, and a standard IT Service Desk fallback when no verified source can respond.

---

## Key Features

### Employee experience

- Enterprise web UI with question form, response panel, and suggested questions sidebar
- **Most Popular** and **Recently Asked** question views (top 10 from DynamoDB)
- `POST /ask` API with JSON responses and server-side validation (max 500 characters)
- Grounded answering with fallback when no verified source applies
- Mock mode (`USE_MOCK_ANSWER=true`) for UI and deployment testing without Bedrock

### IT Portal

- Password-protected workspace for IT Operations (`IT_PORTAL_PASSWORD`)
- **Analytics** tab — question usage metrics from DynamoDB; delete affects analytics only
- **Knowledge Base** tab — view, search, add, edit, and delete FAQ entries in the S3 CSV
- Manual **Sync Knowledge Base** workflow — changes save to S3 immediately; Bedrock ingestion is triggered separately
- Pending-sync banner, toasts, and leave protection when Knowledge Base changes are unsynced

### Operations and deployment

- Docker and Docker Compose for consistent runtime
- Gunicorn WSGI server in production containers
- Styled error pages and toast/modal UI (no browser-default dialogs for application flows)

---

## Architecture

```
Employee browser
       |
       v
Flask Web App (employee UI + IT Portal)
       |
       +-- POST /ask ------------------------------------> Amazon Bedrock
       |                                                      |
       |                                                      v
       |                                            Bedrock Agent (orchestrator)
       |                                                      |
       |                        +-----------------------------+-----------------------------+
       |                        |                             |                             |
       |                        v                             v                             v
       |               Knowledge Base              Action Group:                Fallback response
       |               (S3 CSV + IT docs)          EmployeeSupportServices      (IT Service Desk)
       |                                                      |
       |                                    +-----------------+------------------+
       |                                    |                                    |
       |                                    v                                    v
       |                          getServiceOwner                      lookupIpAddress
       |                                    |                                    |
       |                                    v                                    v
       |                          Lambda:                           Lambda:
       |                          employee_support_services.py       employee_support_services.py
       |                                    |                                    |
       |                                    v                                    v
       |                          DynamoDB ServiceOwners              External public IP API
       |
       +-- IT Portal APIs ----> S3 CSV (read/write) + Bedrock ingestion job
       |
       +-- Analytics ---------> DynamoDB QuestionStats (+ KB sync status record)
```

**Repository integration note:** The Flask application in this repository invokes Amazon Bedrock through the AWS SDK (`bedrock-agent-runtime`) using grounded Knowledge Base retrieval (`retrieve_and_generate`) with strict citation and fallback checks. Bedrock Agent, Action Groups, Lambda, and the ServiceOwners table are companion AWS resources that extend the solution for service-owner and IP lookup questions as described below.

---

## Bedrock Knowledge Base flow

1. **Source content** — FAQ entries live in an S3 CSV object (default key: `it_support_faq_dataset.csv`, configurable via `KNOWLEDGE_BASE_CSV_S3_KEY`) plus supporting IT procedure documents under `knowledge_base/IT/`.
2. **Ingestion** — Bedrock ingests S3 content through a configured data source (`Data_Source_ID_uploadAccount`).
3. **Retrieval** — Employee procedure questions (for example, VPN access steps) are answered from retrieved Knowledge Base content with a grounded prompt (`temperature = 0.0`).
4. **IT Portal updates** — Add, edit, and delete operations update the CSV in S3 immediately.
5. **Manual sync** — **Sync Knowledge Base** in the IT Portal calls `start_ingestion_job` so Bedrock indexes the latest CSV.
6. **Sync status** — A hidden DynamoDB system record (`SYSTEM#KB_SYNC_STATUS`) tracks `isSynced` and **Last Sync Requested**.

---

## Bedrock Agent and Action Groups

The Bedrock Agent orchestrates answering by selecting the appropriate capability:

| Capability | Use case |
|------------|----------|
| **Knowledge Base** | Approved IT procedures and FAQ content from S3 |
| **Action Group tools** | Structured lookups not stored in the FAQ CSV |
| **Fallback** | Standard IT Service Desk message when no verified source applies |

**Action Group name:** `EmployeeSupportServices`

| Function | Purpose |
|----------|---------|
| `getServiceOwner` | Returns the team responsible for an internal service (for example, VPN, GitLab) |
| `lookupIpAddress` | Returns geolocation details for a **public** IP address |

The agent must not answer from general model knowledge when no tool or Knowledge Base source provides a verified result.

---

## Lambda tools

Both Action Group functions are implemented in **`employee_support_services.py`** (AWS Lambda deployment artifact).

### `getServiceOwner`

- Reads from the **ServiceOwners** DynamoDB table
- Matches a normalized service name (for example, `VPN`, `GitLab`)
- Returns team name, contact email, escalation path, and notes when a record exists

### `lookupIpAddress`

- Accepts a candidate IP address from the user question
- Validates **public** IPv4 or IPv6 format before any external call
- Rejects private, reserved, loopback, and malformed addresses
- Calls a public IP geolocation API only after validation succeeds
- Does not treat invalid or private IPs as successful lookup results

---

## DynamoDB tables

### QuestionStats (`QUESTION_STATS_TABLE`)

Used by the Flask application for analytics and Knowledge Base sync status.

| Item type | Partition key | Purpose |
|-----------|---------------|---------|
| Question analytics | `questionId` (SHA-256 of normalized question) | Usage counts, fallback counts, timestamps |
| KB sync status | `SYSTEM#KB_SYNC_STATUS` | Global `isSynced`, `lastSyncRequestedAt` |

Question items use `entityType = QUESTION`. Analytics delete removes tracking data only—not S3 or Bedrock content.

### ServiceOwners

Used by the `getServiceOwner` Lambda tool.

| Setting | Value |
|---------|-------|
| Partition key | `serviceName` (String) |
| Attributes | `teamName`, `contactEmail`, `escalation`, `notes` |

Example: a record for `VPN` enables answers to “Who manages VPN?”

---

## External API integration

The `lookupIpAddress` tool integrates with a **public IP geolocation API** (configured in the Lambda deployment).

Integration rules:

- Validate IPv4/IPv6 syntax and public routability before calling the API
- Do not call the API for private ranges (for example, `10.x`, `172.16–31.x`, `192.168.x`, link-local, or loopback)
- Return a controlled failure path when validation fails so the agent can fall back instead of inventing location data

---

## Fallback and hallucination-prevention behavior

The system is designed to **fail closed** on unverified answers:

1. **Knowledge Base** — Answers use only retrieved content. Missing citations, empty model output, or “cannot find” phrasing maps to the standard IT Service Desk fallback message.
2. **Grounded prompt** — Instructions forbid guessing links, phone numbers, tools, or procedures not present in search results.
3. **Service owner** — If no ServiceOwners record matches, the agent must not invent a team or contact.
4. **IP lookup** — Invalid or private IPs must not produce geolocation results.
5. **Out-of-scope questions** — General knowledge questions (for example, weather) receive the fallback, not a model-generated factual answer.

Standard fallback (paraphrased): contact the IT Service Desk via ServiceNow or the documented support channel—never a hallucinated procedure.

---

## Environment variables

Copy `.env.example` to `.env`. Credentials load **only** from environment variables (via `python-dotenv`), not from `~/.aws/credentials`.

| Variable | Description |
|----------|-------------|
| `FLASK_ENV` | `development` or `production` |
| `FLASK_SECRET_KEY` | Flask session signing key |
| `AWS_ACCESS_KEY_ID` | AWS access key — **required at startup** |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key — **required at startup** |
| `BEDROCK_MODEL_ARN` | Foundation model ARN — **required at startup** |
| `USE_MOCK_ANSWER` | `true` to skip live Bedrock calls |
| `QUESTION_STATS_TABLE` | DynamoDB table for analytics and KB sync status |
| `AWS_REGION_uploadAccount` | Active AWS region |
| `Knowledge_Base_ID_uploadAccount` | Bedrock Knowledge Base ID |
| `Data_Source_ID_uploadAccount` | Bedrock data source ID |
| `Bucket_Name_uploadAccount` | S3 bucket for Knowledge Base documents |
| `IAM_Role_ARN_uploadAccount` | IAM role ARN for the Knowledge Base |
| `IT_PORTAL_PASSWORD` | Shared password for `/it-login` (server-side only) |
| `KNOWLEDGE_BASE_CSV_S3_KEY` | Optional S3 key for the FAQ CSV (default: `it_support_faq_dataset.csv`) |
| `AWS_REGION` | Legacy region (retained; not used when uploadAccount values are set) |
| `BEDROCK_KNOWLEDGE_BASE_ID` | Legacy KB ID (retained; not used when uploadAccount values are set) |

**Active profile:** Runtime uses **uploadAccount** variables for Bedrock, S3, and DynamoDB.

**Lambda / Agent setup (AWS console):** Configure the Bedrock Agent, Action Group `EmployeeSupportServices`, Lambda `employee_support_services.py`, ServiceOwners table, and IAM permissions separately in AWS. Do not commit secrets or resource IDs to source control.

---

## Local run

### Prerequisites

- Python 3.11+
- `.env` with required variables (see `.env.example`)
- IAM permissions for Bedrock Knowledge Base access (mock mode still requires env vars)

### Steps

```bash
cd Smart-Employee-Assistant

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env — set USE_MOCK_ANSWER=true for testing without Bedrock

python app.py
```

Open [http://localhost:5000](http://localhost:5000).

### Production-style local run (Gunicorn)

```bash
gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 4 --timeout 120 app:app
```

---

## Docker run

```bash
cp .env.example .env
# Edit .env before starting the container

docker compose up --build
```

Application URL: [http://localhost:5000](http://localhost:5000)

Stop containers:

```bash
docker compose down
```

---

## EC2 deployment notes

The application **can be deployed on Amazon EC2 using Docker Compose** and a configured `.env` file. Typical steps:

1. Launch an EC2 instance (Amazon Linux 2023 or Ubuntu 22.04) in the same region as your Bedrock resources.
2. Install Docker and Docker Compose; clone this repository.
3. Configure `.env` with uploadAccount variables, credentials, and `USE_MOCK_ANSWER=false` for live Bedrock usage.
4. Run `docker compose up -d`.
5. Place a reverse proxy or load balancer with TLS in front of the app.
6. Restrict security groups to trusted corporate or VPN CIDR ranges.

Deploying the Flask container does not by itself deploy Bedrock Agent, Lambda, or DynamoDB tables—provision those AWS resources separately and align them with the architecture above. Prior coursework deployments used EC2 for validation; stop instances when not in active use to control cost. See the [`screenshots/`](screenshots/) folder for example deployment captures.

---

## Demo questions

Example routing for the full Bedrock Agent solution:

| Employee question | Expected source |
|-------------------|-----------------|
| “How do I request VPN access?” | **Knowledge Base** (S3 FAQ / procedure documents) |
| “Who manages VPN?” | **`getServiceOwner`** → DynamoDB **ServiceOwners** |
| “Where is IP address 8.8.8.8 located?” | **`lookupIpAddress`** → external public IP lookup API |
| “Who manages Salesforce?” | **Fallback** (no verified ServiceOwners / KB match) |
| “What is the weather in London?” | **Fallback** (out of scope; no general-knowledge answers) |

With `USE_MOCK_ANSWER=true`, the Flask app returns keyword-based mock answers for local UI testing instead of live Bedrock responses.

---

## Security notes

- Never commit `.env`, access keys, or real AWS resource IDs to git.
- Rotate `FLASK_SECRET_KEY` and IAM access keys per environment.
- Use IAM least privilege for Bedrock, S3, DynamoDB, and Lambda.
- Keep `FLASK_ENV=production` in deployed environments.
- Validate and sanitize user input server-side; render responses with `textContent` on the client to reduce XSS risk.
- IT Portal authentication uses a shared password suitable for demo and coursework; replace with organizational SSO or MFA for production use.
- The IP lookup tool must reject private addresses before calling external APIs.

---

## Cleanup notes

When decommissioning a demo or lab environment:

1. Stop EC2 instances and release elastic IPs if assigned.
2. Delete or disable Bedrock Agent, Action Groups, and Lambda functions created for the project.
3. Remove Bedrock Knowledge Base data sources and optional Knowledge Base resources.
4. Empty and delete dedicated S3 buckets if no longer needed.
5. Delete DynamoDB tables (`QuestionStats`, `ServiceOwners`) or export data first if required.
6. Remove IAM roles and policies created for Bedrock, Lambda, and EC2 access.
7. Revoke IAM user access keys used for development.

Document resource names in your runbook before deletion. Stop test instances after validation to avoid ongoing charges.

---

## Disclaimer

Company names, URLs, phone numbers, and procedures in the dataset and UI copy are fictional and intended for demonstration, coursework, and portfolio use only.
