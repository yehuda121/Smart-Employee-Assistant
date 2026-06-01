# Smart Employee Assistant

AI-powered internal IT Support assistant for employees. Users submit free-text questions through a web interface; answers are generated from an **Amazon Bedrock Knowledge Base** backed by the corporate IT Support dataset (Amdocs Demo).

---

## Project overview

Smart Employee Assistant is a production-oriented Flask application that connects employees to approved IT procedures—VPN access, password reset, production access, software installation, ServiceNow workflows, and more—using retrieval-augmented generation (RAG) on Amazon Bedrock.

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
2. Attach an **IAM instance profile** with permissions for `bedrock:RetrieveAndGenerate` and related Bedrock actions on your knowledge base.
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

<!-- Add screenshots of the home page and sample Q&A response here -->

| Home page | Sample answer |
|-----------|---------------|
| _Screenshot pending_ | _Screenshot pending_ |

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
