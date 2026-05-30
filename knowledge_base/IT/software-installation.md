# Software Installation on Corporate Devices

## Purpose

This document describes how Amdocs employees request and install approved software applications on corporate-managed laptops and desktops. Centralized software management ensures licensing compliance, security patching, and compatibility with Amdocs standard operating environments.

## Scope

This procedure applies to all Amdocs-managed Windows and macOS devices enrolled in Intune or Jamf MDM. It covers installation of pre-approved catalog applications, department-specific tools, and one-off software requests. Installation of unapproved or pirated software is prohibited under the Acceptable Use Policy (KB-SEC-007).

## Procedure

1. **Check the Amdocs Software Catalog first.** Browse the internal catalog at `https://software.amdocs.internal`. Applications marked **Self-Service** can be installed immediately without a ticket. Click **Install** and the deployment will push to your device within 30 minutes (requires network connectivity and MDM check-in).

2. **Self-Service catalog (macOS).** Open the **Amdocs Self Service** app from Applications. Browse categories (Development, Productivity, Design, Utilities) and click **Install** on the desired application. Common developer tools available include IntelliJ IDEA, Docker Desktop, Postman, and Node.js LTS.

3. **Company Portal (Windows).** Open **Company Portal** from the Start menu. Select **Apps** and install available packages. Visual Studio 2022, SQL Server Management Studio, and PuTTY are commonly requested from this portal.

4. **Submit a software request for non-catalog items.** If the application is not in the catalog, create a ServiceNow ticket under **IT Services > Software > Software Installation Request**. Include the application name, version, vendor website, business justification, and whether a license is already available through your department.

5. **License verification.** IT Software Asset Management (SAM) verifies licensing within 2 business days. If a license must be purchased, the request is routed to your manager for budget approval and to Procurement (KB-FIN-010 Software Procurement).

6. **Security review.** Applications not previously vetted undergo a security assessment by IT Security. This may take 3–5 business days. Applications with known vulnerabilities or excessive permission requirements may be denied.

7. **Installation and confirmation.** Once approved, IT deploys the software via MDM or provides installation instructions. You will receive a ServiceNow notification when installation is complete. Verify functionality and close the ticket.

8. **Request elevated privileges (if needed).** Some development tools require local admin rights. Submit a **Temporary Admin Access Request** (KB-IT-0091) with a maximum duration of 72 hours per request.

## Important Notes

- Do not install software from public download sites, browser extensions outside the approved list, or package managers (Homebrew, Chocolatey) without explicit IT approval.
- Open-source software must be registered in the Amdocs Open Source Registry (OSR) before use in production code.
- Adobe Creative Cloud, MATLAB, and other premium licenses are limited to specific departments. Check with your manager before requesting.
- Virtualization software (VMware Fusion, Parallels) is approved only for Tier 2 and Tier 3 hardware with minimum 32 GB RAM.
- Uninstall unused software through Self Service or Company Portal to free disk space and reduce attack surface.

## Contact Information

- **Software Catalog:** `https://software.amdocs.internal`
- **Software Asset Management:** sam@amdocs.com
- **IT Service Desk:** servicedesk@amdocs.com | Internal ext. 4357
