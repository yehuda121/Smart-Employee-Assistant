# Employee Offboarding

## Purpose

This document defines the offboarding process for Amdocs employees departing the company due to resignation, retirement, termination, or contract end. Structured offboarding protects company assets, ensures knowledge transfer, and maintains compliance with security and legal requirements.

## Scope

This procedure applies to all departing Amdocs employees, including full-time, part-time, and fixed-term contract staff. Managers, IT, HR, Facilities, and Security all have defined responsibilities in the offboarding workflow triggered automatically upon separation entry in Workday.

## Procedure

1. **Initiate separation in Workday.** The employee submits resignation via **Career > Request Separation** (voluntary) or HR initiates involuntary separation. Required fields: last working day, reason, and personal email for final documents. Standard notice period: 30 days (US), 60 days (Israel), per local contract.

2. **Manager actions (within 48 hours).** The manager must: confirm last working day, initiate knowledge transfer plan, identify critical access to revoke early, schedule exit interview (voluntary departures), and notify the project team and stakeholders.

3. **Knowledge transfer (2 weeks before last day).** The departing employee documents: active project status, open Jira tickets, key contacts, credential locations (in team password vault, never personal), and pending deliverables. Upload the **Knowledge Transfer Document** template to the team's SharePoint site.

4. **IT access revocation (last working day).** At 18:00 local time on the last working day (or immediately for involuntary terminations):
   - Active Directory account disabled
   - Email converted to shared mailbox (forwarded to manager for 30 days)
   - VPN, GitLab, production, and SaaS access revoked
   - MDM remote wipe initiated on corporate devices

5. **Return company assets.** Return laptop, badge, credit card, tokens, and any other Amdocs property to IT/Facilities. Remote employees receive a prepaid shipping label via email. All assets must be returned within 5 business days of last working day.

6. **HR exit processing.** HR conducts exit interview (voluntary), provides COBRA/benefits continuation information, final paycheck timeline, and non-compete/non-solicitation reminders (if applicable). Final pay includes accrued unused vacation (where required by law).

7. **Access certification.** Security team runs an automated access audit 48 hours post-departure to verify complete deprovisioning. Any remaining access is flagged as a security incident.

8. **Alumni network.** Voluntary departures in good standing receive an invitation to the Amdocs Alumni Network (`https://alumni.amdocs.com`) for networking and boomerang rehire consideration.

## Important Notes

- Garden leave: employees on garden leave retain system access restrictions per Legal guidance. Contact `hr-ops@amdocs.com` for specifics.
- Do not copy company data to personal devices or email accounts during notice period. DLP monitoring is heightened for departing employees.
- Rehire eligibility: employees who leave in good standing are eligible for rehire after 6 months. Involuntary terminations for cause may be flagged ineligible.
- Contractor offboarding follows an abbreviated timeline: access revoked on contract end date, no exit interview.
- Questions about final pay, equity vesting, or benefits: contact `payroll@amdocs.com`.

## Contact Information

- **HR Operations (Offboarding):** hr-ops@amdocs.com
- **IT Service Desk (asset return):** servicedesk@amdocs.com | Internal ext. 4357
- **Security (access concerns):** security@amdocs.com
- **Payroll:** payroll@amdocs.com
