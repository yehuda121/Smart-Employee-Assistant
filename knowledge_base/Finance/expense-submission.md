# Expense Submission in Concur

## Purpose

This document describes the standard procedure for submitting business expense reports through SAP Concur at Amdocs. Timely and accurate expense reporting ensures employee reimbursement, proper cost allocation, and compliance with Amdocs financial policies and tax regulations.

## Scope

This procedure applies to all Amdocs employees submitting out-of-pocket business expenses for reimbursement. Expenses charged to the Amdocs corporate credit card (KB-FIN-003) are auto-imported into Concur but still require report submission with receipt attachment and business purpose documentation.

## Procedure

1. **Access Concur.** Log in to SAP Concur at `https://concur.amdocs.com` using Okta SSO. Ensure your default bank account for reimbursement is current in Workday **Pay > Payment Elections**.

2. **Create an expense report.** Navigate to **Expense > Create New Report**. Use naming convention: `{LastName}_{Purpose}_{MonthYear}` (e.g., `Smith_ClientVisit_May2026`). Link to a pre-approved travel authorization if the expense is travel-related (KB-FIN-002).

3. **Add expense entries.** For each expense, click **Add Expense** and enter:
   - Expense type (Meals, Ground Transport, Office Supplies, Software, Training, etc.)
   - Transaction date
   - Amount and currency (Concur auto-converts to your home currency)
   - Vendor/merchant name
   - Business purpose (minimum 10 characters, specific to the business activity)
   - Cost center (CC-XXXX-DEPT) and project code (PRJ-XXXX) if applicable

4. **Attach receipts.** Upload a clear photo or PDF of the itemized receipt for every expense over $25 USD (or local equivalent). Receipt must show: vendor, date, items, and amount. Missing receipts require a **Missing Receipt Affidavit** (available in Concur) with manager approval.

5. **Review policy compliance.** Concur automatically flags out-of-policy items (e.g., meal exceeding daily limit, unapproved expense type). Address flags before submission — add justification or split personal/business portions.

6. **Submit for approval.** Click **Submit Report**. Approval routing:
   - Expenses under $500: manager approval only
   - $500–$5,000: manager → finance reviewer
   - Over $5,000: manager → finance reviewer → department budget owner

7. **Track reimbursement.** After final approval, reimbursement is processed within 5–7 business days to your Workday bank account. Track status under **Expense > Manage Expenses > Process Reports**.

## Important Notes

- **Submission deadline:** Expenses must be submitted within 30 days of incurring. Late submissions (30–90 days) require director approval. Over 90 days: rejected.
- **Non-reimbursable expenses:** alcohol (unless client entertainment pre-approved), personal travel extensions, traffic fines, gym memberships (use wellness benefit instead), childcare, and political contributions.
- **Meal limits:** Breakfast $20, Lunch $30, Dinner $50 (or per diem — see KB-HR-009). Client entertainment meals require attendee names and business purpose.
- **Expense delegates:** Assistants may be configured as delegates in Concur to submit on behalf of executives. Delegate setup: Concur > Profile > Expense Delegates.
- **Tax compliance:** VAT/GST receipts required for reclaim in EU, UK, Israel, and India. Ensure tax invoices (not just payment receipts) are attached.

## Contact Information

- **Concur Portal:** `https://concur.amdocs.com`
- **Travel & Expense Team:** travel-expense@amdocs.com
- **Finance Helpdesk:** finance-help@amdocs.com | Internal ext. 5200
