# VPN Access for Remote Connectivity

## Purpose

This document defines the standard procedure for requesting, configuring, and using Amdocs Virtual Private Network (VPN) access. VPN connectivity enables employees and approved contractors to securely access internal applications, shared drives, and development environments when working outside Amdocs office locations.

## Scope

This procedure applies to all full-time employees, part-time employees, and approved third-party contractors who require remote access to Amdocs internal resources. VPN access is mandatory for connecting to production systems, internal GitLab repositories, and SharePoint sites labeled Internal or Confidential. Guest WiFi users and visitors without Amdocs credentials are not eligible for VPN access.

## Procedure

1. **Verify eligibility.** Confirm your role requires VPN access. Most engineering, support, and operations staff are pre-approved. Administrative staff may require manager justification.

2. **Submit a VPN access request.** Log in to ServiceNow at `https://amdocs.service-now.com` and navigate to **IT Services > Network Access > VPN Request**. Select your region (EMEA, Americas, APAC) and provide your Amdocs Employee ID (format: ADM-XXXXX), business justification, and expected duration of need.

3. **Obtain manager approval.** Your direct manager receives an automated approval email within 15 minutes. Requests for production environment access additionally require approval from your department's Information Security Liaison (ISL).

4. **Install GlobalProtect client.** Once approved, download the Amdocs GlobalProtect client from the Company Portal (Windows/macOS) or the internal software catalog at `https://software.amdocs.internal`. Do not install VPN clients from public app stores.

5. **Configure connection profile.** Open GlobalProtect and enter the portal address for your region:
   - **Americas:** `vpn-amer.amdocs.com`
   - **EMEA:** `vpn-emea.amdocs.com`
   - **APAC:** `vpn-apac.amdocs.com`

6. **Authenticate with MFA.** Sign in using your Amdocs email (`firstname.lastname@amdocs.com`) and network password. Complete Okta Verify push authentication when prompted.

7. **Validate connectivity.** After connecting, verify access by opening an internal resource such as the Amdocs Wiki (`wiki.amdocs.internal`) or your team's SharePoint site. Run `ping gitlab.amdocs.internal` from a terminal to confirm GitLab reachability.

8. **Disconnect when finished.** Disconnect from VPN when internal resources are no longer needed, especially on personal networks, to reduce unnecessary load on VPN gateways.

## Important Notes

- VPN sessions automatically disconnect after 12 hours of continuous use. Save work before the timeout.
- Split tunneling is enabled by default; only Amdocs-bound traffic routes through the VPN. Do not attempt to disable split tunneling without IT Security approval.
- Concurrent VPN sessions from multiple devices are limited to two per user. A third connection will terminate the oldest session.
- VPN access for contractors expires on the contract end date. Submit a renewal request at least five business days before expiration.
- Report VPN connection failures through ServiceNow under category **Network > VPN Connectivity Issue**. Include your region, error message, and operating system version.

## Contact Information

- **IT Service Desk:** servicedesk@amdocs.com | Internal ext. 4357 | `https://amdocs.service-now.com`
- **Network Operations Center (NOC):** noc@amdocs.com | +1-314-555-0192 (24/7)
- **Information Security Liaison (ISL):** security-liaison@amdocs.com
