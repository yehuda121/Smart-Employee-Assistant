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

## Analytics Charts

The IT Portal **Charts** tab provides read-only analytics dashboards for IT Operations. The charts aggregate existing QuestionStats records in DynamoDB and help teams understand question usage, popular employee needs, fallback patterns, and Knowledge Base coverage gaps.

Available visualizations include **Top Requested IT Topics** (bar chart) and **Fallback Trend** (line chart). Data is loaded through `GET /it-portal/api/analytics/charts` and requires an authenticated IT Portal session.

Operational insights supported by IT Portal analytics and charts:

- **Most Popular Questions** — highlights the highest-volume employee requests to prioritize support and documentation effort
- **Recently Asked Questions** — surfaces current demand and emerging topics from recent activity
- **Fallback Rate / Fallback Questions** — tracks unsupported questions over time to monitor gaps in approved content and tooling
- **Knowledge Base usage insights** — topic aggregation helps identify categories where employees ask frequently but verified answers may be missing or weak

---

## Business Value

Smart Employee Assistant delivers practical value for IT Operations and employees:

- Reduces repetitive IT Service Desk workload by answering common procedure questions automatically
- Gives employees faster access to approved answers through a single self-service entry point
- Improves visibility into recurring IT issues through QuestionStats analytics and IT Portal charts
- Helps IT teams identify missing or weak Knowledge Base content using usage metrics, fallback trends, and topic breakdowns
- Prevents unsupported or hallucinated answers by routing responses through verified Knowledge Base content, registered tools, and standard fallback behavior when no approved source applies

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

**Repository integration note:** The Flask application routes employee questions through Amazon Bedrock Agent (`invoke_agent`) in live mode so the agent can choose Knowledge Base retrieval, Action Group tools, or fallback behavior. Direct Knowledge Base `retrieve_and_generate` remains as a safe fallback if Agent invocation fails. Set `USE_MOCK_ANSWER=true` to bypass Bedrock during local UI testing.

---

## Bedrock Agent Orchestration

In addition to the Amazon Bedrock Knowledge Base, the application uses an Amazon Bedrock Agent to intelligently route requests to the most appropriate source.

The agent can choose between:

- Amazon Bedrock Knowledge Base (IT procedures and FAQs)
- Service ownership lookup tool
- Public IP lookup tool
- Standard fallback response

This allows the assistant to combine retrieval-based answers, structured enterprise data, and real-time external information while preventing unsupported responses.

Typical routing examples:

| User Question | Source |
|--------------|--------|
| How do I request VPN access? | Knowledge Base |
| Who manages VPN? | Service Ownership Tool |
| Where is IP address 8.8.8.8 located? | Public IP Lookup Tool |
| Who manages Salesforce? | Fallback |

---

## Action Groups and Lambda Tools

The Bedrock Agent uses an Action Group named:

EmployeeSupportServices

The Action Group invokes AWS Lambda functions to retrieve information that is not stored in the Knowledge Base.

### Available Functions

#### getServiceOwner

Returns the approved internal owner for an IT service.

Examples:

- Who manages VPN?
- Who owns GitLab?
- Who is responsible for Jira?

Flow:

Employee → Agent → Action Group → Lambda → DynamoDB

#### lookupIpAddress

Returns public network information for a valid IPv4 or IPv6 address using an external public IP information service.

Examples:

- Where is IP address 8.8.8.8 located?
- Look up IP 1.1.1.1

Flow:

Employee → Agent → Action Group → Lambda → External API

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

## ServiceOwners Table

The ServiceOwners table stores approved ownership information for enterprise IT services.

### Primary Key

| Attribute | Type |
|-----------|------|
| serviceName | String |

### Additional Attributes

| Attribute | Description |
|-----------|-------------|
| teamName | Responsible support team |
| contactEmail | Support contact |
| escalation | Escalation path |
| notes | Service-specific ownership details |

Example services:

- VPN
- GitLab
- Jira
- MFA
- ServiceNow
- Production Access
- Email
- WiFi
- SharePoint

---

## External IP Lookup Integration

The assistant supports real-time public IP lookups through an external API accessed by AWS Lambda.

The tool:

- Validates IPv4 and IPv6 addresses
- Rejects invalid addresses
- Retrieves public network information
- Returns geographic and organization details

Typical information returned:

- Country
- Region
- City
- Organization / Network Owner
- Time Zone

Example:

Question:

Where is IP address 8.8.8.8 located?

Result:

The assistant retrieves current public information directly from the external API rather than relying on Knowledge Base content.

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
| `BEDROCK_AGENT_ID` | Bedrock Agent ID for live employee Q&A — **required when `USE_MOCK_ANSWER=false`** |
| `BEDROCK_AGENT_ALIAS_ID` | Bedrock Agent alias ID — **required when `USE_MOCK_ANSWER=false`** |
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

**Lambda / Agent setup (AWS console):** Configure the Bedrock Agent, alias, Action Group `EmployeeSupportServices`, Lambda `employee_support_services.py`, ServiceOwners table, and IAM permissions in AWS. The Flask app invokes the agent in live mode using `BEDROCK_AGENT_ID` and `BEDROCK_AGENT_ALIAS_ID`. Do not commit secrets or resource IDs to source control.

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

## Demonstration Scenarios

### Knowledge Base

Question:

How do I request VPN access?

Source:

Knowledge Base

### DynamoDB Tool

Question:

Who manages VPN?

Source:

ServiceOwners DynamoDB table via Bedrock Agent Action Group

### External API Tool

Question:

Where is IP address 8.8.8.8 located?

Source:

External Public IP Lookup API via Bedrock Agent Action Group

### Fallback

Question:

Who manages Salesforce?

Result:

Standard IT Service Desk fallback response

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
