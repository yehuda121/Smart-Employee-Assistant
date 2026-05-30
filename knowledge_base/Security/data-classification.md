# Data Classification Policy

## Purpose

This document defines the Amdocs data classification framework, which categorizes information assets by sensitivity level and specifies handling requirements for each classification. Proper data classification protects Amdocs intellectual property, customer data, and employee privacy.

## Scope

This policy applies to all Amdocs data regardless of format (electronic, paper, verbal) or storage location (corporate systems, cloud services, personal devices, physical media). All employees are responsible for correctly classifying data they create, process, or store.

## Procedure

1. **Understand classification levels.** Amdocs uses four data classification tiers:

   | Level | Label | Description | Examples |
   |-------|-------|-------------|----------|
   | 1 | **Public** | Approved for public release | Marketing materials, press releases, published documentation |
   | 2 | **Internal** | Amdocs business use only | Internal memos, org charts, project plans, meeting notes |
   | 3 | **Confidential** | Restricted to need-to-know | Customer contracts, financial reports, employee PII, source code |
   | 4 | **Restricted** | Highest sensitivity, strict controls | Production customer data, encryption keys, M&A documents, security audits |

2. **Classify data at creation.** When creating documents, emails, or datasets, apply the appropriate classification label. In Microsoft 365, use **Sensitivity Labels** (Public, Internal, Confidential, Restricted) available in the label dropdown in Word, Excel, Outlook, and SharePoint.

3. **Apply handling requirements by level:**
   - **Public:** No restrictions on sharing or storage
   - **Internal:** Share within Amdocs only. Do not post on public websites or social media
   - **Confidential:** Encrypt at rest and in transit. Share only with authorized individuals. No external sharing without Legal/Security approval. Print only in secure print rooms
   - **Restricted:** Access logged and monitored. No email transmission (use secure file transfer). No printing without CISO approval. No storage on endpoints — use approved secure repositories only

4. **Label physical documents.** Write the classification level in the header or footer of printed documents. Confidential and Restricted printouts must be collected from secure print rooms (KB-IT-009). Shred when no longer needed using cross-cut shredders (blue bins).

5. **Reclassify data when sensitivity changes.** Data may be upgraded (e.g., Internal project plan becomes Confidential upon customer engagement) or downgraded (with data owner and Security approval). Document reclassification in the document metadata or change log.

6. **Handle customer data.** All customer data defaults to **Confidential** minimum. Production customer data (live billing records, subscriber PII) is always **Restricted**. Customer data handling must comply with contractual data processing agreements (DPAs) on file with Legal.

7. **Request classification guidance.** When uncertain, default to the higher classification level and consult your Information Security Liaison (ISL) or email `data-classification@amdocs.com`.

## Important Notes

- Misclassification resulting in data breach may trigger disciplinary action and regulatory notification obligations.
- Microsoft 365 DLP policies automatically detect and block transmission of Restricted data via email and prevent upload to unauthorized cloud services.
- Aggregated data: a collection of Internal items may collectively be Confidential (e.g., employee salary list compiled from individual Internal records).
- Data retention periods vary by classification: Public (indefinite), Internal (7 years), Confidential (per contract/regulation), Restricted (minimum necessary, typically deleted after purpose fulfilled).
- Third-party data received from customers or partners inherits the classification specified in the contract or defaults to Confidential.

## Contact Information

- **Data Classification Team:** data-classification@amdocs.com
- **Information Security:** security@amdocs.com
- **Legal (customer data questions):** legal@amdocs.com
