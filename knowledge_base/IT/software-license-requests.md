# Software License Requests

## Purpose

This document describes the end-to-end process for requesting software licenses at Amdocs. Centralized license management ensures cost control, vendor compliance, audit readiness, and alignment with Amdocs security requirements for third-party software.

## Scope

This procedure applies to all commercial software licenses purchased or allocated by Amdocs, including desktop applications, SaaS subscriptions, development tools, and cloud service licenses. Open-source software without licensing fees follows a separate registration process (KB-IT-005, Section Important Notes).

## Procedure

1. **Check existing availability.** Before requesting a new license, search the Amdocs Software Catalog (`https://software.amdocs.internal/licenses`) to see if your department already holds pool licenses. Contact your department's software coordinator (listed in the catalog) for allocation from existing pools.

2. **Submit a license request.** Create a ServiceNow ticket under **Software > License Request**. Provide: software name and edition, vendor, number of licenses needed, license type (perpetual, subscription, concurrent), business justification, project code, and requested start date.

3. **Manager and budget approval.** Your manager approves the business need. If the annual cost exceeds $5,000 USD, additional approval is required from your department's budget owner (typically a director or VP). Costs under $5,000 are auto-approved if budget exists in the FinOps dashboard.

4. **Security and architecture review.** Software Asset Management (SAM) initiates a review for all new vendors or products not on the Amdocs Approved Software List (ASL). Security review (3–5 days) and Enterprise Architecture review (2–3 days) run in parallel for SaaS products.

5. **Procurement processing.** Approved requests are routed to Procurement (KB-FIN-010). Standard procurement cycle is 10–15 business days for new vendor onboarding and 3–5 days for existing vendor additions.

6. **License provisioning.** Upon purchase, SAM assigns the license to your Employee ID and deploys the software via MDM or sends activation instructions. SaaS licenses are provisioned through Okta SSO integration where supported.

7. **Annual license review.** Department software coordinators conduct annual true-up reviews every November. Unused licenses are reclaimed and redeployed. Employees holding licenses for software they no longer use should notify SAM proactively.

## Important Notes

- Shadow IT (purchasing software on personal credit cards or expensing without SAM approval) is a policy violation subject to disciplinary action.
- License sharing is prohibited. Each user requires an individual named license unless the contract specifies concurrent licensing (e.g., floating MATLAB licenses: 50 concurrent for 200 users).
- Adobe Creative Cloud_all apps: limited to Marketing and Design departments. Engineers requesting Adobe Acrobat Pro should request the Standard edition instead.
- License cost chargeback: licenses over $1,000/year are charged to the requesting department's cost center (format: CC-XXXX-DEPT).
- True-up audits: major vendors (Microsoft, Oracle, JetBrains) audit Amdocs annually. Accurate license assignment is critical to avoid penalty fees.

## Contact Information

- **Software Asset Management:** sam@amdocs.com
- **Procurement (Software):** software-procurement@amdocs.com
- **IT Service Desk:** servicedesk@amdocs.com | Internal ext. 4357
- **FinOps Dashboard:** `https://finops.amdocs.internal`
