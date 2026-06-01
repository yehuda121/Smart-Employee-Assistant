# Smart Employee Assistant

AI-powered internal IT Support assistant for employees. Users submit free-text questions through a web interface; answers are generated from an **Amazon Bedrock Knowledge Base** backed by the corporate IT Support dataset (Amdocs Demo).

---

## Project overview

Smart Employee Assistant is a enterprise-oriented Flask application that connects employees to approved IT procedures—VPN access, password reset, production access, software installation, ServiceNow workflows, and more—using retrieval-augmented generation (RAG) on Amazon Bedrock.

The knowledge base is populated from `dataset/it_support_faq_dataset.csv` and supporting documents in `knowledge_base/IT/`.

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
- `POST /ask` API for asynchronous Q&A with JSON responses
- Amazon Bedrock `retrieve_and_generate` integration via boto3
- Input validation (required, trimmed, max 500 characters)
- Secure error handling without exposing AWS internals to users
- **Mock answer mode** (`USE_MOCK_ANSWER=true`) for UI and Docker testing without Bedrock
- **Most Common Questions** sidebar — top 10 by usage (defaults seeded at count 0; custom successful questions can rank in) (`data/question_stats.json`)
- Docker and Docker Compose for consistent deployment
- Gunicorn WSGI server in production containers

---

## Folder structure

```
Smart-Employee-Assistant/
├── app.py                          # Flask application and Bedrock integration
├── question_stats.py               # Popular-question tracking (JSON persistence)
├── data/
│   └── question_stats.json         # Runtime stats (gitignored; created automatically)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   └── index.html                  # Home page and client-side UX
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
| `AWS_REGION` | AWS region for Bedrock (e.g. `us-east-1`) — **required at startup** |
| `AWS_ACCESS_KEY_ID` | AWS access key — **required at startup** |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key — **required at startup** |
| `BEDROCK_KNOWLEDGE_BASE_ID` | Bedrock Knowledge Base ID — **required at startup** |
| `BEDROCK_MODEL_ARN` | Foundation model ARN for retrieve and generate — **required at startup** |
| `USE_MOCK_ANSWER` | `true` to return mock answers without calling Bedrock |

**AWS authentication** is deterministic: credentials are loaded **only** from environment variables defined in `.env` (via `python-dotenv`). The application does **not** use `~/.aws/credentials`, AWS CLI profiles, or the default boto3 credential chain.

On startup, the app validates that all five AWS/Bedrock variables above are set and exits with a clear error if any are missing. Startup logs include the AWS region, Knowledge Base ID, and authentication source (never secrets).

Never commit `.env` or hardcode credentials in source code.

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
