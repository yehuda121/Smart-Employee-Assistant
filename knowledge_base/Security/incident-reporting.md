# Security Incident Reporting

## Purpose

This document defines the procedure for reporting information security incidents at Amdocs. Prompt and accurate incident reporting enables the Security Operations Center (SOC) to contain threats, minimize damage, and meet regulatory notification requirements.

## Scope

This procedure applies to all Amdocs employees, contractors, and third parties who discover or suspect a security incident. A security incident is any event that compromises or threatens the confidentiality, integrity, or availability of Amdocs information systems or data.

## Procedure

1. **Recognize a security incident.** Common incident types include:
   - Unauthorized access to systems or data
   - Malware or ransomware infection
   - Lost or stolen devices containing Amdocs data
   - Accidental data exposure (emailing Restricted data externally, public cloud upload)
   - Denial of service affecting Amdocs services
   - Physical security breach (tailgating, unauthorized entry)
   - Insider threat indicators

2. **Report immediately — do not investigate alone.** Contact the Amdocs SOC using the fastest available method:
   - **Phone (24/7):** +1-800-236-7621 (1-800-ADM-SOC1)
   - **Email:** security@amdocs.com (for non-urgent incidents)
   - **ServiceNow:** **Security > Report Security Incident** (auto-routes to SOC)
   - **In person:** Corporate Security desk (ext. 4910) for physical incidents

3. **Provide initial information.** Report: your name and contact, date/time of discovery, description of the incident, systems/data affected, actions already taken, and whether the incident is ongoing.

4. **Preserve evidence.** Do not delete files, clear browser history, reformat devices, or modify systems unless directed by the SOC. Disconnect infected devices from the network (unplug Ethernet/disable WiFi) but do not power off (RAM evidence may be lost).

5. **SOC triage and response.** The SOC assigns a severity level and incident number (format: SEC-INC-YYYY-NNNN):
   - **P1 (Critical):** Active breach, ransomware, production data exposure — response within 15 minutes
   - **P2 (High):** Confirmed unauthorized access, malware contained — response within 1 hour
   - **P3 (Medium):** Suspected incident, policy violation — response within 4 hours
   - **P4 (Low):** Minor event, near-miss — response within 24 hours

6. **Cooperate with investigation.** The SOC or Incident Response Team may request: system logs, email headers, screenshots, witness statements, or temporary surrender of devices for forensic imaging. Cooperation is mandatory.

7. **Receive incident closure notification.** Upon resolution, the incident reporter receives a summary (sanitized if Restricted details are involved) and any required remediation actions (password reset, training re-completion).

## Important Notes

- **No retaliation:** Good-faith incident reporting is protected. Employees who report incidents promptly, even if caused by their own error, will not face disciplinary action for the reporting act itself.
- Regulatory notification: Amdocs must notify affected customers and regulators within 72 hours for incidents involving customer PII (GDPR, CCPA). Delayed reporting by employees directly impacts compliance timelines.
- Do not discuss active incidents externally or on public channels (social media, non-Amdocs email). Media inquiries are handled exclusively by Corporate Communications.
- False reporting with malicious intent is a disciplinary offense.
- Post-incident lessons learned are published (sanitized) quarterly in the **Security Bulletin** on the intranet.

## Contact Information

- **SOC Hotline (24/7):** +1-800-236-7621
- **Security Email:** security@amdocs.com
- **Incident Response Team:** ir-team@amdocs.com
- **Corporate Security (physical):** corp-security@amdocs.com | Internal ext. 4910
