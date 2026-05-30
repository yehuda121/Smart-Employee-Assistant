# Service Desk Ticket Submission and Management

## Purpose

This article explains how Amdocs employees create, track, and escalate IT service desk tickets through ServiceNow. Using the Service Desk correctly ensures timely resolution of technology issues and provides audit trails for compliance and service level reporting.

## Scope

This procedure applies to all Amdocs employees and approved contractors who require IT support for hardware, software, network, account, and access-related issues. The Amdocs IT Service Desk operates 24/7/365 with follow-the-sun coverage across EMEA, Americas, and APAC regions.

## Procedure

1. **Access ServiceNow.** Navigate to `https://amdocs.service-now.com` or click the **ServiceNow** icon on the Amdocs intranet homepage. Authenticate with your Amdocs credentials and Okta MFA.

2. **Create a new incident.** Click **Create Incident** or use the global search bar. Select the most specific category and subcategory (e.g., **Hardware > Laptop > Performance Issue**). Vague categories delay routing and resolution.

3. **Provide required details.** Include:
   - Descriptive short description (e.g., "VPN disconnects every 30 minutes on Dell Latitude 5540")
   - Detailed description with steps to reproduce
   - Your Employee ID, location, and device asset tag (found on the silver sticker on your laptop)
   - Business impact (Unable to Work, Degraded, Low Impact)
   - Attach screenshots or error logs if applicable

4. **Submit and note your ticket number.** Upon submission, you receive a ticket number (format: INC0012345) via email. Use this number for all follow-up communication.

5. **Track ticket status.** Monitor progress in the **My Items** dashboard. Status values include New, In Progress, On Hold (awaiting your response), Resolved, and Closed. Respond promptly to **On Hold** tickets to avoid auto-closure after 5 business days.

6. **Use live chat for urgent issues.** For Priority 1 issues (complete inability to work), open live chat from the ServiceNow portal (available 07:00–19:00 in your local region) or call the Service Desk hotline at internal extension 4357.

7. **Escalate unresolved tickets.** If your ticket exceeds the SLA (see Important Notes) without resolution, click **Escalate** on the ticket or email `servicedesk-escalation@amdocs.com` with the ticket number.

8. **Close the loop.** When IT marks your ticket Resolved, test the fix and click **Reopen** if the issue persists or **Close** if satisfied. Unclosed resolved tickets auto-close after 3 business days.

## Important Notes

- **SLA targets:** P1 (Unable to Work): 4-hour response, 8-hour resolution. P2 (Degraded): 8-hour response, 24-hour resolution. P3 (Low Impact): 24-hour response, 72-hour resolution.
- Do not create duplicate tickets for the same issue. Reference the existing ticket number instead.
- Service requests (access, hardware, software) use the **Service Catalog** module, not incidents. Incidents are for break/fix issues only.
- The Service Desk cannot assist with HR, payroll, or facilities issues. Use Workday for HR and ServiceNow Facilities catalog for building issues.
- After-hours P1 support is available globally via the NOC bridge: +1-314-555-0192.

## Contact Information

- **IT Service Desk Portal:** `https://amdocs.service-now.com`
- **Phone:** Internal ext. 4357 | External: +1-314-555-4357
- **Email:** servicedesk@amdocs.com
- **Escalation:** servicedesk-escalation@amdocs.com
