# Secure Remote Access Policy

## Purpose

This document defines security requirements for Amdocs employees accessing corporate resources from remote locations. Secure remote access ensures that working outside Amdocs offices does not create additional risk to company data, systems, or customer information.

## Scope

This policy applies to all remote access to Amdocs internal resources, including VPN connections, cloud console access (AWS, Azure), SaaS applications, and remote desktop sessions. It covers full-time remote workers, hybrid employees on remote days, and employees traveling for business.

## Procedure

1. **Connect via approved VPN only.** All remote access to internal Amdocs resources must route through GlobalProtect VPN (KB-IT-001). Direct internet access to internal systems is blocked by firewall policy. Split tunneling is enabled — only Amdocs-bound traffic uses VPN.

2. **Authenticate with MFA on every session.** Okta MFA (push notification or YubiKey) is required for VPN login, cloud console access, and all Okta-integrated SaaS applications. Do not approve MFA prompts you did not initiate.

3. **Use only managed devices.** Remote access to Amdocs resources is permitted only from:
   - Amdocs-managed laptops (Intune/Jamf enrolled)
   - BYOD devices with Intune App Protection (email and limited apps only — no VPN or production access)
   Personal unmanaged devices cannot connect to VPN or access internal systems.

4. **Secure your home network.**
   - Use WPA2 or WPA3 encryption on your router
   - Change default router admin passwords
   - Keep router firmware updated
   - Do not share your home network with unauthorized users during Amdocs work sessions
   - Optional: create a guest/work VLAN if your router supports it

5. **Access cloud consoles securely.** AWS and Azure console access requires VPN + Okta SSO + MFA. Use IAM roles with least privilege (no root account usage). Session timeout: 8 hours. Do not access cloud consoles from public computers or shared kiosks.

6. **Remote desktop sessions.** Access to internal servers and jump hosts (KB-IT-003) must use CyberArk PAM sessions. Direct RDP/SSH from home networks to internal IPs is blocked. All sessions are recorded.

7. **Prohibited remote access practices:**
   - Connecting to VPN from countries under US/Israel export control sanctions without Legal approval
   - Using public WiFi without VPN (coffee shops, airports, hotels)
   - Sharing your VPN session or allowing family members to use your Amdocs device
   - Storing Amdocs data on personal cloud services or local unencrypted drives
   - Screen sharing your desktop with Restricted data visible during personal video calls

8. **Travel-specific requirements.** When traveling internationally, review the **Travel Security Checklist** at `https://security.amdocs.internal/travel`. High-risk destinations may require a loaner "travel laptop" with limited data (request via ServiceNow 10 days before travel).

## Important Notes

- VPN bandwidth is monitored. Sustained usage exceeding 50 GB/day triggers a Security review (may indicate personal streaming or data exfiltration).
- Amdocs SOC correlates VPN login locations with Workday registered location. Logins from unexpected countries generate automatic alerts.
- Remote access is revoked immediately upon termination (KB-HR-005). Do not attempt to connect after your last working day.
- Screen lock (5 minutes) and full-disk encryption (KB-SEC-006) are mandatory for all remote work devices.
- Quarterly remote access audits verify compliance. Non-compliant devices are quarantined until remediated.

## Contact Information

- **Network Security Team:** network-security@amdocs.com
- **SOC Hotline:** +1-800-236-7621
- **IT Service Desk (VPN issues):** servicedesk@amdocs.com | Internal ext. 4357
