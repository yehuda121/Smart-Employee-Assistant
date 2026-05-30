# Production Environment Access

## Purpose

This document outlines the controlled process for requesting, approving, and maintaining access to Amdocs production systems. Production access is strictly governed to protect customer data, billing systems, and live telecom infrastructure managed by Amdocs platforms.

## Scope

This procedure applies to any employee or contractor who requires read or write access to Amdocs production environments, including production AWS accounts (tagged `env=prod`), production Kubernetes clusters, production databases, and customer-facing Amdocs CES (Customer Experience Suite) deployments. Development and staging environments follow a separate, less restrictive process (KB-IT-0088).

## Procedure

1. **Complete prerequisite training.** Before submitting a request, complete the following courses in the Amdocs Learning Portal (ALP):
   - **PROD-101:** Production Access Fundamentals (annual renewal)
   - **SEC-205:** Handling Customer Data in Production
   - **CHG-110:** Change Management for Production Systems

2. **Submit a Production Access Request (PAR).** In ServiceNow, navigate to **IT Services > Access Management > Production Access Request**. Provide your Employee ID, target system or environment name (e.g., `ces-prod-us-east-1`, `billing-db-prod-emea`), required access level (Read-Only, Read-Write, Admin), and business justification tied to a Jira ticket or change request number.

3. **Obtain multi-level approval.** PARs require sequential approval from:
   - Your direct manager
   - The system owner (listed in the Amdocs CMDB)
   - Information Security (for Read-Write and Admin levels)
   - Change Advisory Board (CAB) liaison (for Admin level only)

4. **Complete Just-In-Time (JIT) provisioning.** Approved access is provisioned through CyberArk Privileged Access Manager. You will receive a time-bound elevation window (default: 4 hours for Read-Write, 8 hours for Read-Only). Admin access is limited to 2-hour windows and requires a live CAB-approved change ticket.

5. **Access production systems.** Connect via the Amdocs jump host (`jump-prod.amdocs.internal`) using your CyberArk session. All production sessions are recorded and monitored by the SOC. Do not bypass the jump host under any circumstances.

6. **Document all actions.** Log every production change in the associated ServiceNow change record. Include timestamps, commands executed, and rollback steps. Read-only access for troubleshooting must still be logged in the Jira incident ticket.

7. **Request access renewal or revocation.** Production access expires after 90 days. Submit a renewal PAR at least 10 business days before expiration. Access is automatically revoked upon role change, transfer, or termination.

## Important Notes

- Emergency break-glass access is available 24/7 through the NOC (+1-314-555-0192) but requires post-incident review within 24 hours.
- Direct SSH or RDP connections to production servers from VPN are blocked by firewall policy.
- Copying production data to non-production environments requires a separate Data Masking Request (KB-SEC-0012).
- Violations of production access policy may result in immediate access revocation and disciplinary action.

## Contact Information

- **Production Access Team:** prod-access@amdocs.com
- **CyberArk Support:** cyberark-support@amdocs.com | Internal ext. 4891
- **Change Advisory Board:** cab@amdocs.com
- **IT Service Desk:** servicedesk@amdocs.com | Internal ext. 4357
