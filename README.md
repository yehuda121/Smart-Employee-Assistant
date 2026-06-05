# Smart Employee Assistant

Internal IT Support assistant for employees. Users submit questions through a web interface; answers are generated from an **Amazon Bedrock Knowledge Base** backed by an IT Support FAQ dataset stored in **Amazon S3** and indexed for retrieval-augmented generation (RAG).

---

## Overview

Smart Employee Assistant is a Flask application that connects employees to approved IT procedures—VPN access, password reset, production access, software installation, ServiceNow workflows, and related topics—using Bedrock Knowledge Base retrieval.

The application has two primary surfaces:

| Surface | Audience | Purpose |
|---------|----------|---------|
| **Employee home** (`/`) | All employees | Ask questions and receive Knowledge Base answers |
| **IT Portal** (`/it-login`, `/it-portal`) | IT Operations | Review question analytics and manage Knowledge Base content |

The Knowledge Base source of truth for FAQ content is a CSV file in S3. Question usage metrics are stored separately in DynamoDB. These layers are intentionally decoupled so analytics changes do not affect indexed content, and vice versa.

---

## Architecture

```
Employee browser
       |
       v
Flask Web App (templates + REST APIs)
       |
       +-- POST /ask  --------------------> Amazon Bedrock Knowledge Base
       |                                        |
       |                                        v
       |                                   S3 CSV + ingested documents
       |
       +-- IT Portal APIs ----------------> S3 CSV (read/write)
       |                                        |
       |                                        +--> Bedrock start_ingestion_job (manual sync)
       |
       +-- Question analytics -------------> DynamoDB (QuestionStats table)
```

**Bedrock Knowledge Base + S3 CSV flow**

1. FAQ entries live in a CSV object in S3 (`KNOWLEDGE_BASE_CSV_S3_KEY`, default `it_support_faq_dataset.csv`).
2. Bedrock ingests that object (and related documents) through a configured data source.
3. Employee questions call Bedrock `retrieve_and_generate` against the indexed content.
4. IT Portal Add/Edit/Delete operations update the CSV in S3 immediately.
5. **Sync Knowledge Base** triggers a Bedrock ingestion job so employee answers reflect the latest CSV.

**DynamoDB QuestionStats analytics**

Each `/ask` request records normalized question text, usage count, fallback count, and timestamps in `QUESTION_STATS_TABLE`. This data powers the employee sidebar and the IT Portal Analytics tab. It does not store answers or user identity.

---

## Features

### Employee experience

- Enterprise web UI with question form, response panel, and suggested questions
- Sidebar dropdown: **Most Popular** or **Recently Asked** questions (top 10 from DynamoDB)
- `POST /ask` API with JSON responses and server-side validation (required, trimmed, max 500 characters)
- Secure error handling without exposing AWS internals to users
- **Mock answer mode** (`USE_MOCK_ANSWER=true`) for UI and deployment testing without Bedrock

### Popular vs Recently Asked questions

The employee sidebar includes a sort control above the question list:

| View | Sort order | API |
|------|------------|-----|
| **Most Popular Questions** (default) | `count` descending | `GET /api/common-questions?sort=popular` |
| **Recently Asked Questions** | `lastAskedAt` descending | `GET /api/common-questions?sort=recent` |

The sidebar displays the top 10 questions for the selected view.

### IT Portal

The IT Portal is a password-protected workspace for IT Operations. Access it from the **IT Team** header link. Authentication uses a shared password (`IT_PORTAL_PASSWORD`) stored server-side in `.env` and validated through a Flask session. This approach is intentionally simple for demo and development use; it is not intended as enterprise-grade access control.

| Route | Purpose |
|-------|---------|
| `/it-login` | Password sign-in |
| `/it-portal` | Analytics and Knowledge Base management |
| `POST /it-logout` | End IT Portal session |
| `DELETE /it-portal/api/analytics/<questionId>` | Delete analytics record (DynamoDB only) |
| `GET/POST/PUT/DELETE /it-portal/api/knowledge` | Knowledge Base CSV CRUD |
| `GET /it-portal/api/knowledge/sync-status` | Current sync state |
| `POST /it-portal/api/knowledge/sync` | Manually trigger Bedrock ingestion |

#### Analytics tab

- Displays question usage from DynamoDB (`QUESTION_STATS_TABLE`)
- Columns include count, fallback count, last asked, and created timestamps
- Interactive column sorting (default: **Count ↓**)
- Delete requires confirmation and shows a success toast
- **Analytics delete affects DynamoDB only** — it does not remove S3 files, CSV rows, Bedrock resources, or indexed Knowledge Base content

#### Knowledge Base Management tab

- Loads FAQ entries from the S3 CSV (`Bucket_Name_uploadAccount`)
- Search, pagination, sort by Question or Category
- Expandable answer previews
- **Add**, **Edit**, and **Delete** entries through modal forms
- Changes save to S3 immediately; Bedrock indexing is a separate manual step

#### Manual Sync workflow

Synchronization state is stored in a hidden DynamoDB system record (`questionId = SYSTEM#KB_SYNC_STATUS`, `entityType = SYSTEM`) in the same table as question analytics. This record is the single source of truth for global Knowledge Base sync status.

| Step | Behavior |
|------|----------|
| Add / Edit / Delete | Updates CSV and uploads to S3 immediately |
| After save | Sets `isSynced = false` on the system record |
| **Sync Knowledge Base** | Calls Bedrock `start_ingestion_job` |
| After sync request succeeds | Sets `isSynced = true` and records **Last Sync Requested** |

Employees only receive updated answers after Bedrock ingestion completes. The portal UI reflects pending state from the system record (`isSynced = false`).

#### Unsynced changes behavior

When `isSynced = false`, the IT Portal:

- Shows a pending synchronization banner on the Knowledge Base tab
- Displays an informational toast when the portal loads
- Prompts before switching away from the Knowledge Base tab, navigating home, or logging out

**Leave-warning flow**

| Action | Warning shown |
|--------|----------------|
| Switch tab, go home, or logout with pending changes | Custom in-app modal (Cancel / Leave Without Syncing / Sync and Leave) |
| Browser refresh or tab close with pending changes | Browser-native `beforeunload` prompt |
| Leave Without Syncing or Sync and Leave (home/logout) after modal confirmation | No second browser-native prompt — navigation proceeds once |

In-app navigation uses the custom modal only. The browser-native warning is reserved for refresh and tab close when the user has not already confirmed through the modal.

#### Analytics delete vs Knowledge delete

| Action | Data affected | S3 / CSV | Bedrock sync required |
|--------|---------------|----------|------------------------|
| Delete analytics record | DynamoDB `QuestionStats` only | No | No |
| Delete knowledge entry | CSV row in S3 | Yes (saved immediately) | Yes (until **Sync Knowledge Base** is run) |

Wrong passwords show a generic error. AWS errors are logged server-side and never exposed to users.

---

## Folder structure

```
Smart-Employee-Assistant/
├── app.py                          # Flask application and Bedrock integration
├── aws_config.py                   # uploadAccount active AWS configuration
├── knowledge_base_service.py       # S3 CSV Knowledge Base CRUD and Bedrock sync
├── question_stats.py               # Analytics tracking and KB sync system record
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── templates/
│   ├── index.html                  # Employee home page
│   ├── it_login.html               # IT Portal login
│   └── it_portal.html              # IT Portal workspace
├── static/
│   ├── css/styles.css
│   └── js/
│       ├── portal-ui.js            # Modals and toasts
│       └── it-portal.js            # IT Portal tab logic
├── dataset/it_support_faq_dataset.csv
├── knowledge_base/IT/              # Supporting procedure documents
└── screenshots/                    # UI and deployment documentation
```

---

## Environment variables

Copy `.env.example` to `.env` and configure:

| Variable | Description |
|----------|-------------|
| `FLASK_ENV` | `development` or `production` |
| `FLASK_SECRET_KEY` | Flask session signing key |
| `AWS_ACCESS_KEY_ID` | AWS access key — **required at startup** |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key — **required at startup** |
| `BEDROCK_MODEL_ARN` | Foundation model ARN for retrieve and generate — **required at startup** |
| `USE_MOCK_ANSWER` | `true` to return mock answers without calling Bedrock |
| `QUESTION_STATS_TABLE` | DynamoDB table for analytics and KB sync status — **required at startup** |
| `AWS_REGION_uploadAccount` | Active AWS region — **required at startup** |
| `Knowledge_Base_ID_uploadAccount` | Active Bedrock Knowledge Base ID — **required at startup** |
| `Data_Source_ID_uploadAccount` | Active Bedrock data source ID — **required at startup** |
| `Bucket_Name_uploadAccount` | S3 bucket for Knowledge Base documents — **required at startup** |
| `IAM_Role_ARN_uploadAccount` | IAM role ARN for the Knowledge Base — **required at startup** |
| `IT_PORTAL_PASSWORD` | Shared password for `/it-login` (server-side only) |
| `KNOWLEDGE_BASE_CSV_S3_KEY` | Optional S3 key for the FAQ CSV (default: `it_support_faq_dataset.csv`) |
| `AWS_REGION` | Legacy region (retained in `.env`; not used when uploadAccount values are set) |
| `BEDROCK_KNOWLEDGE_BASE_ID` | Legacy Knowledge Base ID (retained in `.env`; not used when uploadAccount values are set) |

**Active AWS profile:** The application uses **uploadAccount** variables for Bedrock, S3, and DynamoDB. Legacy `AWS_REGION` and `BEDROCK_KNOWLEDGE_BASE_ID` remain in `.env` for reference but are not read at runtime.

**Authentication:** Credentials are loaded only from environment variables (via `python-dotenv`). The application does not use `~/.aws/credentials`, AWS CLI profiles, or the default boto3 credential chain.

On startup, the app validates required uploadAccount variables, credentials, `BEDROCK_MODEL_ARN`, and `QUESTION_STATS_TABLE`, then exits with a clear error if any are missing. Never commit `.env` or hardcode credentials.

### DynamoDB table setup

Create the table in the same region as `AWS_REGION_uploadAccount`:

| Setting | Value |
|---------|-------|
| Table name | Value of `QUESTION_STATS_TABLE` (e.g. `QuestionStats`) |
| Partition key | `questionId` (String) |
| Billing | On-demand recommended for demo workloads |

**Question analytics items** use `entityType = QUESTION`. The partition key `questionId` is a SHA-256 hash of the normalized question text. Items include `questionText`, `count`, `fallbackCount`, `createdAt`, `updatedAt`, and `lastAskedAt`.

**KB sync status** uses a hidden system item: `questionId = SYSTEM#KB_SYNC_STATUS`, `entityType = SYSTEM`, with `isSynced`, `lastSyncRequestedAt`, and `updatedAt`.

On every `/ask` request, `count` is incremented and `lastAskedAt` is updated. `fallbackCount` increments only when the answer is the standard KB fallback message. If the table is empty at startup, 10 common IT Support questions are seeded once. If DynamoDB is unavailable, Q&A continues and the sidebar returns an empty list.

**IAM permissions:** The principal needs `dynamodb:PutItem`, `UpdateItem`, `GetItem`, `Scan`, and `DeleteItem` on the table; `s3:GetObject` and `s3:PutObject` on the Knowledge Base bucket; and `bedrock:StartIngestionJob` on the active data source.

---

## Run locally

### Prerequisites

- Python 3.11+
- A `.env` file with all required variables (see `.env.example`)
- IAM credentials with Bedrock Knowledge Base access (mock mode still requires env vars to be set)

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

## Run with Docker

```bash
cp .env.example .env
# Edit .env (USE_MOCK_ANSWER=true recommended until Bedrock is configured)

docker compose up --build
```

Application URL: [http://localhost:5000](http://localhost:5000)

Stop containers:

```bash
docker compose down
```

---

## Deploy on Amazon EC2 (overview)

1. Launch an EC2 instance (Amazon Linux 2023 or Ubuntu 22.04) in the same region as your Bedrock Knowledge Base.
2. Install Docker and Docker Compose, clone this repository, and configure `.env`.
3. Set `USE_MOCK_ANSWER=false` for live Knowledge Base queries.
4. Run `docker compose up -d` and place a load balancer or reverse proxy (nginx) in front with TLS.
5. Restrict security groups to corporate network or VPN CIDR ranges.

On EC2, inject the same variables into `.env` or the container environment. This application does not read instance metadata or `~/.aws/credentials` automatically.

Do not expose the instance directly to the public internet without appropriate network controls and TLS.

---

## Public deployment (test instance)

The application was successfully tested at:

http://3.239.124.41:5000

The EC2 instance was stopped after testing to avoid unnecessary AWS charges.

---

## Mock answer mode

Set `USE_MOCK_ANSWER=true` in `.env` when:

- The Bedrock Knowledge Base is still being created or synced
- You are testing the UI, Docker image, or deployment pipeline
- AWS credentials are unavailable on your machine

Mock responses use keyword matching against common IT Support topics. Set `USE_MOCK_ANSWER=false` for live Bedrock answers.

---

## Knowledge base dataset

The IT Support FAQ CSV (`dataset/it_support_faq_dataset.csv`) contains 90 entries with columns: `id`, `category`, `question`, `answer`, `keywords`, `source_document`. Upload to S3 and connect to your Bedrock Knowledge Base data source, or convert rows to documents for ingestion.

---

## Screenshots

The following images document the Smart Employee Assistant UI, Amazon Bedrock Knowledge Base configuration, and EC2 deployment workflow. All screenshots are stored in the [`screenshots/`](screenshots/) directory.

### Web application (Flask)

Enterprise home page with the question form, **Most Common Questions** analytics sidebar, and internal IT Support branding.

![Smart Employee Assistant — Flask web application home page](screenshots/Flask%20app.png)

*Figure 1 — Local Flask application: ask-a-question workspace and Most Common Questions panel.*

---

### Amazon Bedrock Knowledge Base

Knowledge Base resource in the AWS console and successful data source synchronization after ingesting the IT Support dataset.

![Amazon Bedrock Knowledge Base in the AWS console](screenshots/knowledge%20base%20on%20AWS.png)

*Figure 2 — Bedrock Knowledge Base configured for IT Support content.*

![Knowledge Base data source sync completed successfully](screenshots/sync%20success.png)

*Figure 3 — Data source sync status after uploading FAQ / procedure documents to S3.*

---

### EC2 deployment and operations

End-to-end deployment on Amazon EC2: instance setup, cloning the repository, Docker installation, and the application running in production.

> **Note:** After all EC2 deployment screenshots and application validation were completed, the instance was stopped to avoid ongoing compute charges. This stop action is recommended for non-production test environments when the host is not in active use.

![EC2 instance — initial setup](screenshots/EC2%20first%20initial.png)

*Figure 4 — EC2 environment prepared for application deployment.*

![Clone project repository on EC2](screenshots/clone%20project%20from%20git%20using%20EC2%20.png)

*Figure 5 — Project cloned from Git on the EC2 host.*

![EC2 terminal after Docker installation](screenshots/ec2%20terminal%20after%20docker%20installation.png)

*Figure 6 — Docker installed and ready to run the containerized Flask app.*

![Smart Employee Assistant running on EC2](screenshots/the%20app%20running%20on%20EC2.png)

*Figure 7 — Application accessible on EC2 (port 5000 / load balancer as configured).*

---

### Q&A examples on EC2 (successful Knowledge Base answers)

Sample employee questions with grounded answers returned from the Knowledge Base via Bedrock.

![EC2 — successful Knowledge Base answer (example 1)](screenshots/(EC2)%20getting%20an%20answer.png)

*Figure 8 — Successful response generated from retrieved IT procedures.*

![EC2 — successful Knowledge Base answer (example 2)](screenshots/(EC2)%20getting%20an%20answer%202.png)

*Figure 9 — Additional successful Q&A session on EC2.*

![EC2 — successful Knowledge Base answer (example 3)](screenshots/(EC2)%20getting%20an%20answer%203.png)

*Figure 10 — Follow-up question with Knowledge Base–grounded answer.*

---

### Q&A examples on EC2 (fallback responses)

When the Knowledge Base does not contain a relevant match, the application returns the standard IT Service Desk fallback message (no general-knowledge answers).

![EC2 — fallback response when no KB match (example 1)](screenshots/(EC2)%20getting%20an%20answer%20(fallback)1.png)

*Figure 11 — Fallback message displayed when retrieval cannot answer from the knowledge base.*

![EC2 — fallback response when no KB match (example 2)](screenshots/(EC2)%20getting%20an%20answer%20(fallback)2.png)

*Figure 12 — Fallback behavior for out-of-scope or unmatched employee questions.*

---

### Screenshot index

| File | Description |
|------|-------------|
| `Flask app.png` | Local Flask UI — question form and Most Common Questions sidebar |
| `knowledge base on AWS.png` | Bedrock Knowledge Base in AWS console |
| `sync success.png` | Successful Knowledge Base data source sync |
| `EC2 first initial.png` | EC2 initial deployment setup |
| `clone project from git using EC2 .png` | Git clone on EC2 |
| `ec2 terminal after docker installation.png` | Docker ready on EC2 |
| `the app running on EC2.png` | Application running on EC2 |
| `(EC2) getting an answer.png` | Successful KB answer (example 1) |
| `(EC2) getting an answer 2.png` | Successful KB answer (example 2) |
| `(EC2) getting an answer 3.png` | Successful KB answer (example 3) |
| `(EC2) getting an answer (fallback)1.png` | Fallback response (example 1) |
| `(EC2) getting an answer (fallback)2.png` | Fallback response (example 2) |

---

## Resources cleanup

After testing and documentation were completed:

- EC2 instance was stopped.
- Security groups remained for documentation purposes.
- Bedrock Knowledge Base remained available for future testing.
- No additional AWS resources were left running unintentionally.

When decommissioning the environment, remove or archive resources in this order:

1. Bedrock Knowledge Base data source sync jobs
2. Bedrock Knowledge Base and associated data source
3. S3 bucket objects and bucket (if dedicated to this project)
4. IAM roles and policies created for Bedrock / EC2 access
5. OpenSearch Serverless or Aurora resources if provisioned for the knowledge base
6. EC2 instances, load balancers, and security groups used for hosting

Document your actual resource IDs in your team runbook before deletion.

---

## Security notes

- Rotate `FLASK_SECRET_KEY` per environment.
- Use IAM least privilege for Bedrock and S3 access.
- Rotate `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` on a regular schedule.
- Keep `FLASK_ENV=production` in deployed environments.
- User input is validated server-side; responses are rendered with `textContent` on the client to prevent XSS.
- IT Portal access uses a shared password suitable for demo use. For production deployments, replace this with your organization's standard authentication mechanism.

---

## Support

For application issues, contact your platform team. For IT policy content, use the corporate Service Desk (ServiceNow) or servicedesk@amdocs.com.

---

## Disclaimer

Company names, URLs, and procedures in the dataset are fictional and intended for demonstration and development.
