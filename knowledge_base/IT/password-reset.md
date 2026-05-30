# Password Reset Procedure

## Purpose

This article describes how Amdocs employees reset forgotten or expired network passwords and regain access to corporate systems including email, VPN, Okta MFA, and workstation login. Following this procedure ensures password changes comply with Amdocs security policy and propagate correctly across integrated systems.

## Scope

This procedure covers password resets for all Amdocs Active Directory accounts associated with `@amdocs.com` email addresses. It applies to employees in all regions. Separate procedures exist for external partner accounts (see KB-IT-0142) and service accounts (managed by IT Operations only).

## Procedure

1. **Attempt self-service reset first.** Navigate to `https://password.amdocs.internal` from any browser. Click **Forgot Password** and enter your Amdocs email address and Employee ID (ADM-XXXXX).

2. **Verify identity via Okta.** If you still have access to your registered Okta Verify device, approve the push notification. If your phone is unavailable, select **Alternative Verification** and answer your pre-configured security questions (minimum three correct answers required).

3. **Create a new password.** Your new password must meet Amdocs policy requirements: minimum 14 characters, at least one uppercase letter, one lowercase letter, one number, one special character, and no reuse of the last 12 passwords. Passwords must not contain your name, Employee ID, or the word "Amdocs."

4. **Confirm synchronization.** After resetting, wait up to 10 minutes for password propagation. Test login on your workstation, Outlook, and VPN in that order.

5. **Locked account recovery.** If your account is locked after five failed login attempts, self-service reset automatically unlocks the account upon successful password change. If self-service fails, proceed to Step 6.

6. **Contact the Service Desk for assisted reset.** Call the IT Service Desk at internal extension 4357 or submit a ticket under **Account Management > Password Reset – Assisted**. Be prepared to verify identity with your Employee ID, last four digits of the phone number on file in Workday, and your manager's name.

7. **Update saved credentials.** After resetting, update passwords stored in password managers, mobile email apps, and any automated scripts that authenticate with your AD credentials. Failure to update saved credentials is the most common cause of re-lockouts.

## Important Notes

- Passwords expire every 90 days. You will receive email reminders at 14, 7, and 1 day(s) before expiration via `noreply-security@amdocs.com`.
- Never share your password with anyone, including IT staff. Legitimate Amdocs IT will never ask for your password.
- If you suspect your password was compromised, immediately reset it via self-service and report the incident to security@amdocs.com (see KB-SEC-003 Incident Reporting).
- Mac users on Amdocs-managed devices may need to log out and back in, or run `sudo jamf policy` from Terminal, to refresh the local login keychain after a password change.
- Contractors whose accounts are managed by a vendor manager must contact their vendor liaison rather than using self-service.

## Contact Information

- **Self-Service Portal:** `https://password.amdocs.internal`
- **IT Service Desk:** servicedesk@amdocs.com | Internal ext. 4357
- **Information Security:** security@amdocs.com | SOC Hotline: +1-800-236-7621
