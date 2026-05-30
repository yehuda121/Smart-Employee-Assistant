# Device Encryption Requirements

## Purpose

This document defines Amdocs requirements for full-disk encryption on all devices that store or access Amdocs data. Device encryption protects data at rest against unauthorized access in the event of device loss, theft, or improper disposal.

## Scope

This policy applies to all corporate-managed laptops, desktops, mobile devices (phones and tablets enrolled in MDM), and external storage media used for Amdocs business. Personal devices accessing Amdocs data via BYOD must also comply with encryption requirements enforced through Intune App Protection Policies.

## Procedure

1. **Corporate device encryption (automatic).** All Amdocs-managed devices are encrypted automatically during provisioning:
   - **Windows:** BitLocker with TPM 2.0, AES-256 encryption. Recovery keys escrowed in Azure AD/Intune
   - **macOS:** FileVault 2, AES-256 encryption. Recovery keys escrowed in Jamf
   - **iOS/Android:** Hardware-level encryption enforced via MDM enrollment (mandatory for Amdocs email access)

2. **Verify encryption status.** Employees can verify their device is encrypted:
   - **Windows:** Settings > Privacy & Security > Device Encryption (should show "On"), or run `manage-bde -status` in Command Prompt
   - **macOS:** System Settings > Privacy & Security > FileVault (should show "On")
   - **Mobile:** Enrolled in Intune/Jamf — encryption is enforced automatically

3. **Report encryption failures.** If encryption is not active (e.g., after OS reinstallation or hardware repair), do not use the device for Amdocs work. Submit a ServiceNow ticket under **Security > Device Encryption Issue**. IT will re-enable encryption or replace the device.

4. **External storage media.** USB drives and external hard drives used for Amdocs data must be Amdocs-issued encrypted devices (Kingston IronKey or Apricorn Aegis, available via KB-SEC-009 USB Device Usage). Personal USB drives must not store Amdocs data.

5. **Encryption during repair or transfer.** Before sending a device for repair (KB-IT-013), IT verifies encryption is active. Devices sent to vendors for repair are shipped with encryption enabled; recovery keys are not shared with vendors. Data wipe precedes any device decommissioning.

6. **Lost or stolen encrypted devices.** Report immediately to security@amdocs.com (KB-SEC-003). Encrypted devices are significantly lower risk, but remote wipe is still initiated via MDM within 30 minutes. Provide the device asset tag and last known location.

7. **BYOD encryption verification.** Personal devices accessing Amdocs email or data via Intune App Protection must have device encryption enabled (verified during enrollment). Non-compliant devices are blocked from accessing Amdocs applications.

## Important Notes

- Disabling BitLocker or FileVault on corporate devices is blocked by MDM policy and constitutes a security violation.
- BitLocker recovery keys are accessible to IT administrators for legitimate recovery. Employees should not store recovery keys locally on the same device.
- Encryption does not protect data while the device is powered on and unlocked. Screen lock (5-minute timeout) and Clean Desk Policy (KB-SEC-005) provide additional protection.
- Performance impact of encryption on modern hardware (TPM-accelerated AES) is negligible (<2% on Amdocs standard devices).
- Devices that cannot support encryption (legacy hardware without TPM) are decommissioned and replaced — they are not exempt.

## Contact Information

- **Endpoint Security Team:** endpoint-security@amdocs.com
- **IT Service Desk:** servicedesk@amdocs.com | Internal ext. 4357
- **Information Security:** security@amdocs.com
