# Amdocs Password Policy

## Purpose

This document defines Amdocs requirements for password creation, management, and protection across all corporate systems. Strong password practices are a foundational security control protecting Amdocs and customer data from unauthorized access.

## Scope

This policy applies to all Amdocs Active Directory passwords, application-specific passwords, service account passwords (managed by IT Operations), and passwords for SaaS applications integrated with Okta SSO. Personal passwords for non-Amdocs services used on corporate devices are encouraged to follow these guidelines.

## Procedure

1. **Password requirements.** All Amdocs passwords must meet the following minimum criteria:
   - Minimum 14 characters in length
   - At least one uppercase letter (A–Z)
   - At least one lowercase letter (a–z)
   - At least one numeric digit (0–9)
   - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
   - Must not contain: user's first or last name, Employee ID, "Amdocs", or dictionary words alone
   - Must not match any of the previous 12 passwords (password history)

2. **Password expiration.** Passwords expire every 90 days. Expiration notifications are sent to `@amdocs.com` email at 14, 7, and 1 day(s) before expiration from `noreply-security@amdocs.com`. Expired passwords require reset via `https://password.amdocs.internal` (KB-IT-002).

3. **Use approved password managers.** Amdocs provides 1Password Business licenses to all employees. Store work passwords exclusively in 1Password. Do not store passwords in browsers (except Okta SSO sessions), spreadsheets, sticky notes, or unencrypted files.

4. **Create unique passwords per system.** Do not reuse Amdocs passwords on external sites, personal accounts, or non-Amdocs services. For systems not integrated with Okta SSO, generate unique passwords using 1Password's password generator (20+ characters recommended).

5. **Protect passwords during use.** Never share passwords via email, Teams chat, phone, or in person. Never enter your Amdocs password on non-Amdocs websites (phishing prevention). Use privacy screens in public locations.

6. **Report compromised passwords immediately.** If you suspect your password has been disclosed, reset it immediately via self-service and report to security@amdocs.com. Change passwords on any external accounts where the same password was reused.

7. **Service account passwords.** Service account passwords are managed exclusively by IT Operations and rotated automatically every 60 days via CyberArk. Developers must not embed service account credentials in code or configuration files.

## Important Notes

- Account lockout occurs after 5 consecutive failed login attempts. Lockout duration: 30 minutes, or immediate unlock via self-service password reset.
- Passphrases are encouraged (e.g., "Correct-Horse-Battery-Staple-2026!") as they are easier to remember and harder to crack.
- Okta SSO eliminates the need for separate passwords on most Amdocs applications. Prefer SSO over standalone credentials wherever available.
- Passwords are never stored in plaintext by Amdocs systems. IT staff cannot retrieve your password — only reset it.
- Violations (sharing passwords, writing passwords on whiteboards, using weak passwords that bypass policy via technical means) may result in disciplinary action up to termination.

## Contact Information

- **Password Self-Service:** `https://password.amdocs.internal`
- **Information Security:** security@amdocs.com
- **IT Service Desk:** servicedesk@amdocs.com | Internal ext. 4357
