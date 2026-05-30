# Multi-Factor Authentication (MFA) Setup

## Purpose

This article provides step-by-step instructions for enrolling in and managing Multi-Factor Authentication (MFA) at Amdocs. MFA is a mandatory security control that protects employee accounts and corporate resources from unauthorized access by requiring a second verification factor beyond the network password.

## Scope

MFA enrollment is required for all Amdocs employees, contractors with AD accounts, and any user accessing VPN, email, ServiceNow, GitLab, or cloud consoles (AWS, Azure). The primary MFA platform at Amdocs is Okta Verify with push notification as the default factor. Hardware tokens (YubiKey) are available for roles requiring FIPS-compliant authentication.

## Procedure

1. **Receive enrollment notification.** New employees receive an MFA enrollment email from `okta-admin@amdocs.com` within 24 hours of account creation. The email contains a one-time enrollment link valid for 72 hours.

2. **Download Okta Verify.** Install Okta Verify on your registered mobile device (iOS or Android) from the official app store. Do not use third-party authenticator apps unless explicitly approved for your role.

3. **Complete initial enrollment.** Click the enrollment link or navigate to `https://amdocs.okta.com`. Sign in with your Amdocs credentials. When prompted, open Okta Verify on your phone and scan the QR code displayed on screen.

4. **Register a backup factor.** After primary enrollment, you must register at least one backup factor:
   - **Secondary device:** Install Okta Verify on a backup phone or tablet
   - **Hardware token:** Request a YubiKey 5 NFC from IT via ServiceNow (**Account Management > MFA Hardware Token**)
   - **Security questions:** Configure three security questions in Okta (least preferred; acceptable only when mobile device is unavailable)

5. **Test MFA on key systems.** Verify MFA prompts appear when logging into:
   - Amdocs VPN (GlobalProtect)
   - Outlook Web Access (`https://mail.amdocs.com`)
   - ServiceNow and GitLab

6. **Replace or transfer MFA when changing devices.** Before decommissioning a phone, log in to `https://amdocs.okta.com`, navigate to **Settings > Security Methods**, and add your new device. Remove the old device only after confirming the new one works.

7. **Recover locked MFA access.** If you lose access to all MFA factors, contact the IT Service Desk for identity verification and temporary bypass code issuance. Bypass codes are single-use and expire after 24 hours.

## Important Notes

- MFA push notifications must be approved within 60 seconds or the login attempt fails.
- Never approve an Okta push notification you did not initiate. Report unexpected prompts to security@amdocs.com immediately.
- Okta Verify requires a device PIN or biometric lock. Devices without screen lock are non-compliant and will be blocked.
- Contractors must enroll within 48 hours of account activation or the account will be suspended.
- Travelers to regions with restricted app store access should request a YubiKey at least 10 business days before travel.

## Contact Information

- **Okta Admin Team:** okta-admin@amdocs.com
- **IT Service Desk:** servicedesk@amdocs.com | Internal ext. 4357
- **Information Security:** security@amdocs.com
