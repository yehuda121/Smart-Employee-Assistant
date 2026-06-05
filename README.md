# Smart Employee Assistant

AI-powered internal IT Support assistant for employees. Users submit free-text questions through a web interface; answers are generated from an **Amazon Bedrock Knowledge Base** backed by the corporate IT Support dataset (Amdocs Demo).

---

## Project overview

Smart Employee Assistant is a enterprise-oriented Flask application that connects employees to approved IT procedures—VPN access, password reset, production access, software installation, ServiceNow workflows, and more—using retrieval-augmented generation (RAG) on Amazon Bedrock.

The knowledge base is populated from `dataset/it_support_faq_dataset.csv` and supporting documents in `knowledge_base/IT/`.

---

## Topic

Internal IT Support Knowledge Assistant (Amdocs Demo)

---

## Architecture

```
User
  |
  v
Flask Web App (templates + REST /ask)
  |
  v
boto3 (bedrock-agent-runtime)
  |
  v
Amazon Bedrock Knowledge Base
  |
  v
S3 Dataset (ingested FAQ / procedure documents)
  |
  v
Generated Answer returned to the user
```

---

## Features

- Modern enterprise web UI with question form, response panel, and suggested questions
- Sidebar dropdown: **Most Popular** or **Recently Asked** questions (top 10 from DynamoDB)
- `POST /ask` API for asynchronous Q&A with JSON responses
- Amazon Bedrock `retrieve_and_generate` integration via boto3
- Input validation (required, trimmed, max 500 characters)
- Secure error handling without exposing AWS internals to users
- **Mock answer mode** (`USE_MOCK_ANSWER=true`) for UI and Docker testing without Bedrock
- **Question analytics** in **Amazon DynamoDB** (`QUESTION_STATS_TABLE`) with `lastAskedAt` tracking
- **IT Portal** (`/it-login`, `/it-portal`) — password-protected analytics dashboard with sort and delete
- Docker and Docker Compose for consistent deployment
- Gunicorn WSGI server in production containers

---

## Folder structure

```
Smart-Employee-Assistant/
├── app.py                          # Flask application and Bedrock integration
├── aws_config.py                   # uploadAccount active AWS configuration
├── question_stats.py               # Popular-question tracking (DynamoDB)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   ├── index.html                  # Employee home page and client-side UX
│   ├── it_login.html               # IT Portal password login
│   └── it_portal.html              # IT analytics dashboard
├── static/
│   └── css/
│       └── styles.css
├── screenshots/                    # UI, AWS, and EC2 documentation images
├── dataset/
│   └── it_support_faq_dataset.csv  # IT Support FAQ dataset for Bedrock ingestion
└── knowledge_base/
    └── IT/                         # Source procedure documents
```

---

## Environment variables

Copy `.env.example` to `.env` and configure:

| Variable | Description |
|----------|-------------|
| `FLASK_ENV` | `development` or `production` |
| `FLASK_SECRET_KEY` | Flask session signing key (use a long random value in production) |
| `AWS_ACCESS_KEY_ID` | AWS access key — **required at startup** |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key — **required at startup** |
| `BEDROCK_MODEL_ARN` | Foundation model ARN for retrieve and generate — **required at startup** |
| `USE_MOCK_ANSWER` | `true` to return mock answers without calling Bedrock |
| `QUESTION_STATS_TABLE` | DynamoDB table name for Most Common Questions (partition key: `questionId`) — **required at startup** |
| `AWS_REGION_uploadAccount` | Active AWS region for Bedrock, S3, and DynamoDB — **required at startup** |
| `Knowledge_Base_ID_uploadAccount` | Active Bedrock Knowledge Base ID — **required at startup** |
| `Data_Source_ID_uploadAccount` | Active Bedrock data source ID — **required at startup** |
| `Bucket_Name_uploadAccount` | Active S3 bucket for Knowledge Base documents — **required at startup** |
| `IAM_Role_ARN_uploadAccount` | IAM role ARN used by the Knowledge Base / upload account — **required at startup** |
| `AWS_REGION` | Legacy region (retained in `.env`; not used when uploadAccount values are set) |
| `BEDROCK_KNOWLEDGE_BASE_ID` | Legacy Knowledge Base ID (retained in `.env`; not used when uploadAccount values are set) |
| `IT_PORTAL_PASSWORD` | Shared password for the demo IT Portal login at `/it-login` (not exposed to the browser) |

**Active AWS profile:** The application uses the **uploadAccount** variables above for Bedrock queries, S3/Knowledge Base context, and DynamoDB question analytics. Legacy `AWS_REGION` and `BEDROCK_KNOWLEDGE_BASE_ID` remain in `.env` for reference but are not read at runtime.

**AWS authentication** is deterministic: credentials are loaded **only** from environment variables defined in `.env` (via `python-dotenv`). The application does **not** use `~/.aws/credentials`, AWS CLI profiles, or the default boto3 credential chain.

On startup, the app validates all required uploadAccount variables, credentials, `BEDROCK_MODEL_ARN`, and `QUESTION_STATS_TABLE`, then exits with a clear error if any are missing. Startup logs include the active region, Knowledge Base ID, data source ID, S3 bucket, DynamoDB table, and authentication source (never secrets).

Never commit `.env` or hardcode credentials in source code.

### DynamoDB — Question analytics

Each submitted question is normalized (trim, lowercase, collapse spaces) and stored in `QUESTION_STATS_TABLE` using the **uploadAccount** region and credentials. The partition key `questionId` is a SHA-256 hash of `normalizedQuestion`. Items include `questionText`, `normalizedQuestion`, `count`, `fallbackCount`, `entityType` (`QUESTION`), `createdAt`, `updatedAt`, and `lastAskedAt`.

On every `/ask` request, `count` is incremented, `updatedAt` and `lastAskedAt` are set to the current UTC ISO timestamp, and `fallbackCount` is incremented only when the final answer is the KB fallback message. If the table is empty at startup, 10 common IT Support questions are seeded once with `count = 1`, `fallbackCount = 0`, and matching `createdAt`, `updatedAt`, and `lastAskedAt` timestamps (existing items are not duplicated). If DynamoDB is unavailable, the application continues to serve Q&A and returns an empty question list.

**Employee sidebar — Popular vs Recent**

The right-hand sidebar includes a dropdown above the question list:

| View | Sort order |
|------|------------|
| **Most Popular Questions** (default) | `count` descending |
| **Recently Asked Questions** | `lastAskedAt` descending |

The sidebar shows the top 10 questions for the selected view. Changing the dropdown reloads the list from `GET /api/common-questions?sort=popular|recent`.

**IT Portal (demo login)**

IT staff can open the analytics dashboard from the **IT Team** link in the header (routes to `/it-login` or `/it-portal` depending on session state).

| Route | Purpose |
|-------|---------|
| `/it-login` | Password-only login using `IT_PORTAL_PASSWORD` from `.env` (stored in Flask session) |
| `/it-portal` | Full analytics table with sort controls: Most Popular, Most Fallbacks, Recently Asked |
| `POST /it-logout` | Clears IT Portal session |

This is demo authentication only — not production-grade identity management. Wrong passwords show a generic error; AWS errors are logged server-side and never exposed to users.

**Delete analytics (DynamoDB only)**

From `/it-portal`, IT staff can delete individual question analytics records after confirmation. Delete removes only the DynamoDB `QuestionStats` item — it does **not** delete S3 objects, CSV source data, Bedrock resources, or Knowledge Base content.

Create the table in the same region as `AWS_REGION_uploadAccount`:

| Setting | Value |
|---------|-------|
| Table name | Value of `QUESTION_STATS_TABLE` (e.g. `QuestionStats`) |
| Partition key | `questionId` (String) |
| Billing | On-demand recommended for demo workloads |

The IAM principal needs `dynamodb:PutItem`, `dynamodb:UpdateItem`, `dynamodb:GetItem`, `dynamodb:Scan`, and `dynamodb:DeleteItem` on the table.

---

## Run locally

### Prerequisites

- Python 3.11+
- A `.env` file with all required AWS and Bedrock variables (see `.env.example`)
- IAM user or role keys with Bedrock Knowledge Base access (mock mode still requires env vars to be set)

### Steps

```bash
# Clone and enter the project
cd Smart-Employee-Assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set USE_MOCK_ANSWER=true for testing without Bedrock

# Run the application
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
2. Configure AWS credentials and Bedrock settings using environment variables.
3. Install Docker and Docker Compose, clone this repository, and configure `.env` with `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and Bedrock settings.
4. Set `USE_MOCK_ANSWER=false` for live Knowledge Base queries.
5. Run `docker compose up -d` and place an Application Load Balancer or reverse proxy (nginx) in front with TLS.
6. Restrict security groups to corporate network or VPN CIDR ranges.

On EC2, inject the same variables into `.env` or the container environment. This application does not read instance metadata or `~/.aws/credentials` automatically.

Do not expose the instance directly to the public internet without authentication and TLS.

---

## Public Deployment

The application was successfully tested on:

http://3.239.124.41:5000

The EC2 instance was stopped after testing to avoid unnecessary AWS charges.

---

## Mock answer mode

Set `USE_MOCK_ANSWER=true` in `.env` when:

- The Bedrock Knowledge Base is still being created or synced
- You are testing the UI, Docker image, or deployment pipeline
- AWS credentials are unavailable on your machine

Mock responses use keyword matching against common IT Support topics and reference Amdocs Demo procedures. Set `USE_MOCK_ANSWER=false` for live Bedrock answers.

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

## Resources Cleanup

After testing and documentation were completed:

- EC2 instance was stopped.
- Security groups remained for documentation purposes.
- Bedrock Knowledge Base remained available for future testing.
- No additional AWS resources were left running unintentionally.

---

## AWS resource cleanup

When decommissioning the environment, remove or archive resources in this order to avoid orphaned charges:

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
- Use IAM least privilege for Bedrock and S3 access; scope keys to Bedrock Knowledge Base actions only.
- Rotate `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` on a regular schedule.
- Keep `FLASK_ENV=production` in deployed environments.
- User input is validated server-side; responses are rendered with `textContent` on the client to prevent XSS.

---

## Support

For application issues, contact your platform team. For IT policy content, use the corporate Service Desk (ServiceNow) or servicedesk@amdocs.com.

---

## Disclaimer

Company names, URLs, and procedures in the dataset are fictional and intended for demonstration and development.
