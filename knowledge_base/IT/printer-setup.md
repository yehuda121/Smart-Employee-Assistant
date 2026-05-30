# Printer Setup and Usage

## Purpose

This document provides instructions for configuring and using printers at Amdocs office locations and for setting up secure printing from remote locations. Following this procedure ensures print jobs are routed through Amdocs managed print infrastructure with appropriate audit and cost controls.

## Scope

This procedure applies to all Amdocs employees who need to print, scan, or copy documents at office locations or via secure cloud printing. It covers Ricoh and HP multifunction devices deployed at Amdocs facilities globally. Personal printer installation on corporate devices is not supported except for approved home office setups (see Section 7).

## Procedure

1. **Install the Amdocs print driver (office printing).** On Amdocs-managed devices, the **Amdocs-Global-Print** queue is deployed automatically via MDM. Verify it appears in your system print dialog. If missing, install from the Software Catalog (KB-IT-005).

2. **Authenticate at the printer.** Walk to any Amdocs multifunction printer (MFP). Tap your Amdocs badge on the RFID reader, or enter your Employee ID and network password on the touchscreen. Your queued jobs will appear on the display.

3. **Release print jobs.** After sending a document to **Amdocs-Global-Print**, it is held in a secure queue for up to 24 hours. Go to any MFP on any Amdocs floor, authenticate, select your jobs, and tap **Print**. Jobs not released within 24 hours are automatically deleted.

4. **Configure scan-to-email.** At the MFP, select **Scan**, choose **Scan to Email**, and authenticate. Scans are sent to your `@amdocs.com` mailbox as PDF attachments. Maximum scan size is 50 pages per job.

5. **Locate printers by office.** Printer locations are listed in the Amdocs Facilities Map (`https://facilities.amdocs.internal/maps`). Ra'anana HQ printers follow naming convention `RH-FL{floor}-PR{number}` (e.g., `RH-FL3-PR07`).

6. **Submit a printer issue ticket.** For paper jams, toner alerts, or connectivity problems, scan the QR code on the printer to auto-create a ServiceNow ticket, or submit manually under **Facilities > Printer Support**.

7. **Home office printer setup (approved roles only).** Employees approved for permanent remote work may request a home printer allocation (HP LaserJet Pro, one per household). Submit a ServiceNow request under **Hardware > Home Office Printer**. The device must connect via VPN for driver deployment and usage is logged.

## Important Notes

- Color printing requires manager approval and is tracked by cost center. Default queue is black-and-white, double-sided.
- Printing classified documents (Confidential or Restricted per KB-SEC-002) requires use of MFPs in secure print rooms with badge access logging.
- Do not print customer PII unless necessary for approved business processes. Shred printed PII using designated cross-cut shredders (blue bins).
- Monthly print quotas: 500 pages (B&W) and 100 pages (color) per employee. Exceeding quotas requires cost center manager approval for overage.
- Mobile printing is supported via the **Ricoh Smart Device Connector** app for iOS/Android on Amdocs-managed mobile devices.

## Contact Information

- **Print Services Team:** print-services@amdocs.com
- **IT Service Desk:** servicedesk@amdocs.com | Internal ext. 4357
- **Facilities (printer supplies):** facilities@amdocs.com | Internal ext. 4600
