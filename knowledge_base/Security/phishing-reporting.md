# Phishing Reporting Procedure

## Purpose

This document describes how Amdocs employees identify, report, and respond to phishing emails and social engineering attempts. Phishing is the most common attack vector targeting Amdocs employees, and rapid reporting protects the entire organization.

## Scope

This procedure applies to all Amdocs employees and contractors who receive suspicious emails at their `@amdocs.com` address or via Teams, SMS, or phone calls impersonating Amdocs personnel or systems. It covers external phishing and internal account compromise (business email compromise).

## Procedure

1. **Recognize phishing indicators.** Common signs include:
   - Sender address that mimics but does not match Amdocs domains (e.g., `@amdocss.com`, `@arndocs.com`)
   - Urgent language demanding immediate action ("Your account will be deleted in 24 hours")
   - Unexpected attachments or links, especially `.html`, `.zip`, `.exe`, or URL shorteners
   - Requests for credentials, MFA codes, or financial transfers
   - Poor grammar, formatting inconsistencies, or generic greetings ("Dear Employee")
   - Emails from executives requesting gift cards, wire transfers, or confidential data

2. **Do not interact with suspicious content.** Do not click links, open attachments, reply, or forward the email (except as directed below). Do not enter credentials on pages linked from suspicious emails, even if the page looks like the Amdocs login screen.

3. **Report using the Outlook plugin (preferred).** Select the suspicious email in Outlook and click the **Report Phishing** button in the ribbon (red fish icon). This automatically forwards the email to the SOC, removes it from your inbox, and submits it for automated analysis.

4. **Report via email (alternative).** Forward the suspicious email as an attachment (not inline) to `phishing@amdocs.com`. Include the full email headers if possible (Outlook: open email > File > Properties > copy Internet Headers).

5. **Report other channels.** For phishing via Teams, SMS, or phone:
   - Teams: click **... > Report Suspicious** on the message
   - SMS/Phone: email details to `phishing@amdocs.com` with date, time, caller ID, and message content
   - Do not block the number yourself — the SOC may need to trace it

6. **If you clicked a link or entered credentials.** Report immediately to the SOC hotline (+1-800-236-7621) even if you already reported the email. Reset your password at `https://password.amdocs.internal` and approve any Okta push notifications only if you initiated the login.

7. **Await SOC response.** The SOC analyzes reported emails within 30 minutes during business hours. If the email is confirmed malicious, a company-wide block is applied and a security advisory is issued. You receive a confirmation email on your report status.

## Important Notes

- Amdocs IT and Security will **never** ask for your password, MFA code, or remote access to your computer via unsolicited email or phone call.
- Simulated phishing exercises are conducted quarterly by the Security Awareness team. Clicked links in simulations trigger mandatory micro-training but do not result in disciplinary action.
- Repeated failures in phishing simulations (3+ clicks in 12 months) require completion of **SEC-210: Advanced Phishing Defense** and a manager notification.
- External senders on the Amdocs approved vendor list still cannot request credential changes via email.
- Report suspected phishing even if you are unsure — false positives are preferred over missed threats.

## Contact Information

- **Phishing Report Email:** phishing@amdocs.com
- **SOC Hotline (if credentials compromised):** +1-800-236-7621
- **Security Awareness Team:** security-awareness@amdocs.com
