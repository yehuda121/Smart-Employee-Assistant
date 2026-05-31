# Smart Employee Assistant — IT Support Knowledge Base

This project provides a demo **IT Support** knowledge base for the fictional **Amdocs Demo** internal company environment. It is designed to power a RAG-based employee assistant using **Amazon Bedrock Knowledge Base**.

## Scope

The knowledge base covers **IT Support only**, including topics such as:

- VPN and remote access
- Password reset and MFA
- Service Desk (ServiceNow) procedures
- Hardware requests and replacements
- Email, SharePoint, and collaboration tools
- Software installation and licensing
- WiFi, printing, GitLab, and production access

HR, Facilities, Security, Finance, and other non-IT domains have been removed from this project.

## Dataset

The primary dataset is stored as a CSV file:

```
dataset/it_support_faq_dataset.csv
```

### CSV schema

| Column | Description |
|--------|-------------|
| `id` | Unique FAQ identifier (e.g., `IT-001`) |
| `category` | IT topic category |
| `question` | Employee question |
| `answer` | Company-specific answer based on internal procedures |
| `keywords` | Semicolon-separated search keywords |
| `source_document` | Reference to the originating IT procedure document |

The dataset contains **90 FAQ entries** derived from Amdocs Demo IT procedures.

## Source documents

Original IT procedure documents are kept in:

```
knowledge_base/IT/
```

These markdown files serve as the source material for the FAQ dataset and can also be ingested directly into a knowledge base.

## Amazon Bedrock Knowledge Base

The CSV dataset is suitable for RAG ingestion with Amazon Bedrock Knowledge Base. You can:

1. **Upload the CSV directly** — Bedrock supports structured data sources; map columns to metadata and content fields during ingestion.
2. **Convert to documents** — Transform each row (or group rows by `source_document`) into text or markdown files for S3-based ingestion.

Example document text per row:

```
Category: VPN Access
Question: How do I request VPN access at Amdocs?
Answer: Log in to ServiceNow at https://amdocs.service-now.com ...
Keywords: VPN;remote access;ServiceNow;manager approval
Source: vpn-access.md
```

Configure your Bedrock Knowledge Base data source (S3 or custom connector), choose an embedding model, and connect it to your retrieval-augmented generation application.

## Project structure

```
Smart-Employee-Assistant/
├── dataset/
│   └── it_support_faq_dataset.csv    # IT Support FAQ dataset (CSV)
├── knowledge_base/
│   └── IT/                           # IT procedure source documents
└── README.md
```

## Disclaimer

This is a **demo dataset** for educational and development purposes. Company names, URLs, email addresses, and procedures are fictional.
