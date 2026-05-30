# Shared Drive and SharePoint Access

## Purpose

This document describes the process for requesting and managing access to Amdocs shared drives, SharePoint sites, and Teams-connected document libraries. Controlled access ensures employees can collaborate on documents while protecting sensitive business and customer information.

## Scope

This procedure applies to all Amdocs SharePoint Online sites, OneDrive shared libraries, and legacy network shares migrated to SharePoint (UNC paths ending in `.sharepoint.com`). It covers Internal, Confidential, and Restricted data classifications as defined in KB-SEC-002 Data Classification.

## Procedure

1. **Identify the resource.** Determine the exact SharePoint site URL or shared drive name. Site URLs follow the pattern `https://amdocs.sharepoint.com/sites/{site-name}`. Ask your project lead or check the Amdocs Project Directory (`https://projects.amdocs.internal`) if unsure.

2. **Request access via ServiceNow.** Submit a ticket under **Access Management > SharePoint / Shared Drive Access**. Provide the site URL, requested permission level (Read, Contribute, Edit, Full Control), business justification, and associated project code (format: PRJ-XXXX).

3. **Obtain owner approval.** The SharePoint site owner (listed on the site homepage under **Site Information**) receives an automated approval request. Access requests for Confidential or Restricted sites additionally require Information Security approval.

4. **Receive access confirmation.** Upon approval, access is provisioned within 4 business hours. You will receive an email confirmation with a direct link to the site. Access is granted through Amdocs AD security groups (naming convention: `SP-{SiteName}-{PermissionLevel}`).

5. **Access shared drives from Windows.** Migrated shares appear as mapped drives (e.g., `S:` for Shared, `P:` for Projects) after group membership syncs. Force a sync by running `gpupdate /force` or logging out and back in. Mac users access SharePoint via browser or OneDrive sync client.

6. **Sync with OneDrive client.** Install the OneDrive sync client (pre-deployed on managed devices). Navigate to the SharePoint site, click **Sync**, and files appear in File Explorer under `{Organization} > {Site Name}`.

7. **Request access removal or modification.** When changing roles or leaving a project, submit an access removal request or ask the site owner to remove you from the AD group. Access reviews are conducted quarterly by site owners.

## Important Notes

- External sharing (outside `@amdocs.com`) requires site owner approval and is limited to Confidential data or below. Restricted data cannot be externally shared.
- Default site storage quota is 256 GB. Requests for additional storage require VP-level approval.
- Do not download Restricted documents to local devices unless approved via exception request to security@amdocs.com.
- Legacy UNC paths (`\\amdocs-files\...`) redirect to SharePoint; update bookmarks and scripts accordingly.
- Orphaned sites (no activity for 12 months) are archived automatically. Contact the Collaboration Team to restore archived content.

## Contact Information

- **Collaboration Team:** collaboration@amdocs.com
- **IT Service Desk:** servicedesk@amdocs.com | Internal ext. 4357
- **Information Security (Restricted access):** security@amdocs.com
