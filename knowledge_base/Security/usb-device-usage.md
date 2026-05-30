# USB Device Usage Policy

## Purpose

This document defines Amdocs policy and procedures for the use of USB and other removable storage devices. Removable media is a common vector for data exfiltration and malware introduction; this policy balances business needs with security controls.

## Scope

This policy applies to all USB storage devices (flash drives, external hard drives, SD cards), USB-connected peripherals with storage capability, and other removable media (CD/DVD, tape) connected to Amdocs-managed devices or used to store Amdocs data.

## Procedure

1. **Default policy: USB storage blocked.** Amdocs-managed devices block unauthorized USB mass storage devices by default via MDM policy (CrowdStrike Device Control). Inserting an unauthorized USB drive will trigger a block notification and a SOC alert.

2. **Request authorized USB device.** Employees requiring USB storage for business purposes must:
   - Submit a ServiceNow request under **Security > USB Device Authorization**
   - Specify business justification and data classification level
   - Obtain manager and Information Security Liaison (ISL) approval
   - Receive an Amdocs-approved encrypted USB device (Kingston IronKey D300 or Apricorn Aegis Secure Key)

3. **Register the device.** Approved USB devices must be registered in the Amdocs Asset Management system. IT applies a device-specific whitelist entry allowing only that serial number on your assigned laptop. Unregistered devices remain blocked.

4. **Use encrypted devices only.** Only Amdocs-issued FIPS 140-2 Level 3 encrypted USB drives may store Amdocs data. Personal USB drives, even if encrypted, are not authorized. Data copied to USB must match the classification level the device was approved for.

5. **Transfer data securely.** When transferring data via USB:
   - Copy only the minimum data required
   - Verify data classification is appropriate for removable media (Restricted data requires CISO approval)
   - Delete data from the USB drive after transfer is complete
   - Do not leave USB drives unattended or connected when not actively transferring

6. **USB peripherals (non-storage).** Standard USB peripherals (keyboards, mice, monitors, docking stations) are permitted without authorization. USB charging cables (power-only) are permitted. USB devices with unknown storage capability (promotional giveaways, conference swag) must not be connected — submit to Security for analysis if needed.

7. **Lost or stolen USB devices.** Report immediately to security@amdocs.com. Amdocs-issued encrypted drives can be cryptographically erased remotely if they connect to an internet-enabled device. Provide the device serial number and last known contents.

8. **Return upon departure.** Return all Amdocs-issued USB devices to IT during offboarding (KB-HR-005). Devices are securely wiped and decommissioned.

## Important Notes

- Exceptions for development teams requiring frequent USB access (hardware testing, firmware loading) are managed through department-level ISL bulk approvals with annual recertification.
- USB boot is disabled on all Amdocs devices via BIOS/UEFI policy.
- Copying customer production data to USB is prohibited unless explicitly approved by the CISO with a documented business case.
- Violations (using unauthorized USB, copying Restricted data without approval) are treated as security incidents (KB-SEC-003).
- Alternatives to USB: use SharePoint, OneDrive, or the Amdocs Secure File Transfer portal (`https://sft.amdocs.internal`) for data sharing.

## Contact Information

- **Information Security:** security@amdocs.com
- **Endpoint Security Team:** endpoint-security@amdocs.com
- **IT Service Desk:** servicedesk@amdocs.com | Internal ext. 4357
