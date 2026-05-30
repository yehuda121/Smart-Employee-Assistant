# Email Configuration for Amdocs Accounts

## Purpose

This knowledge base article describes how to configure and access Amdocs corporate email across supported clients and devices. Amdocs email is hosted on Microsoft 365 and serves as the primary communication channel for internal and external business correspondence.

## Scope

This procedure applies to all Amdocs employees with `@amdocs.com` mailboxes. It covers Outlook desktop, Outlook Web Access (OWA), Outlook mobile, and Apple Mail on Amdocs-managed devices. Configuration on unsupported clients (Thunderbird, legacy POP/IMAP) is not permitted.

## Procedure

1. **Access email on Amdocs-managed Windows devices.** Outlook is pre-installed and auto-configured via Intune. Open Outlook, enter your `@amdocs.com` address when prompted, and authenticate with your network password and Okta MFA. Autodiscover resolves settings to `outlook.office365.com`.

2. **Access email on Amdocs-managed Mac devices.** Outlook for Mac is deployed via Jamf. Launch Outlook and sign in with your Amdocs credentials. If auto-configuration fails, manually set the server to `outlook.office365.com` with OAuth2 authentication (not basic auth).

3. **Access email via web browser.** Navigate to `https://mail.amdocs.com` or `https://outlook.office.com`. Sign in with your Amdocs email and complete Okta MFA. OWA provides full email, calendar, and contacts functionality without local installation.

4. **Configure Outlook mobile (iOS/Android).** Install Microsoft Outlook from the official app store. Add account using your `@amdocs.com` address. When redirected to Okta, authenticate and approve the MFA push. Intune App Protection Policies automatically apply, separating Amdocs data from personal apps.

5. **Set up email signatures.** Amdocs requires standardized email signatures. Download the template for your region from the Brand Portal (`https://brand.amdocs.internal/signatures`). Required fields: full name, job title, department, office location, phone number, and the Amdocs legal disclaimer footer.

6. **Configure shared mailboxes and distribution lists.** Access to shared mailboxes (e.g., `project-alpha@amdocs.com`) requires a ServiceNow request under **Account Management > Shared Mailbox Access**. Distribution list membership is managed by list owners via the Exchange Admin self-service portal at `https://lists.amdocs.internal`.

7. **Set up out-of-office replies.** Configure automatic replies in OWA under **Settings > Mail > Automatic Replies**. Include your backup contact and expected return date. For absences exceeding 5 business days, also update your status in Microsoft Teams.

## Important Notes

- Mailbox quota is 100 GB per user. Archive mailboxes (auto-enabled after 2 years) provide an additional 100 GB.
- External email forwarding to personal accounts is blocked by DLP policy.
- Maximum attachment size is 25 MB via email; use SharePoint or OneDrive links for larger files.
- Phishing reporting: use the **Report Phishing** button in Outlook or forward suspicious emails to `phishing@amdocs.com` (see KB-SEC-004).
- Email retention: all mailboxes are subject to 7-year retention for compliance. Deleted items are recoverable for 30 days via **Recover Deleted Items** in OWA.

## Contact Information

- **Messaging Team:** messaging@amdocs.com
- **IT Service Desk:** servicedesk@amdocs.com | Internal ext. 4357
- **Exchange Admin Portal:** `https://lists.amdocs.internal`
