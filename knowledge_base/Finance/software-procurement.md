# Software Procurement

## Purpose

This document defines the end-to-end process for procuring software at Amdocs, from initial request through vendor onboarding, licensing, deployment, and ongoing cost management. Centralized software procurement ensures security compliance, license optimization, and budget control.

## Scope

This procedure applies to all commercial software acquisitions including SaaS subscriptions, perpetual licenses, open-source support contracts, cloud platform services, and software maintenance renewals. Free/open-source software without licensing costs follows KB-IT-005 (registration only). Individual license requests follow KB-IT-015.

## Procedure

1. **Check existing licenses and alternatives.** Before initiating procurement:
   - Search the Amdocs Software Catalog (`https://software.amdocs.internal/licenses`) for available pool licenses
   - Check the Approved Software List (ASL) for vetted alternatives
   - Consult your department software coordinator and Enterprise Architecture for recommended solutions

2. **Submit a Software Procurement Request.** Create a ServiceNow ticket under **Software > Software Procurement Request** (or initiate a requisition in Ariba for known vendors). Include:
   - Software name, vendor, and edition
   - License model (per-user, concurrent, site, usage-based)
   - Number of licenses and contract term (1-year, 3-year)
   - Business justification and project code
   - Estimated cost (attach vendor quote if available)
   - Data classification of data the software will process (KB-SEC-002)

3. **Review and approval chain.**
   - **Software Asset Management (SAM):** License model validation, existing contract check (2 days)
   - **Information Security:** Security assessment for new vendors/products (3–5 days, KB-FIN-005)
   - **Enterprise Architecture:** Integration and standards compliance (2–3 days)
   - **Manager + Budget Owner:** Business need and budget approval
   - **Procurement:** Vendor negotiation and contract (5–15 days)

4. **Vendor onboarding (new vendors only).** If the vendor is not on the Approved Vendor List, initiate vendor onboarding (KB-FIN-005) in parallel with the procurement request. Software vendors handling Confidential+ data must provide SOC 2 Type II reports.

5. **Contract and PO issuance.** Procurement negotiates pricing (Amdocs enterprise agreements exist with Microsoft, AWS, JetBrains, Atlassian, and 200+ vendors). A PO is issued through Ariba (KB-FIN-009) or a SaaS order form is signed by authorized signatory (VP+ for contracts over $100K).

6. **License provisioning.** Upon PO/contract completion:
   - SAM registers licenses in the Asset Management system
   - Okta SSO integration configured (for SaaS products)
   - MDM deployment package created (for desktop software)
   - License keys delivered to requester or auto-deployed

7. **Renewal management.** SAM tracks all software contract renewal dates. Renewal notifications are sent 90, 60, and 30 days before expiration to the Vendor Owner and department software coordinator. Auto-renewal contracts require explicit opt-out 30 days before renewal.

8. **Annual true-up and optimization.** Every November, SAM conducts a license true-up: compares purchased licenses vs. active deployments. Unused licenses are reclaimed. Under-licensing triggers true-up purchases with vendor audit risk mitigation.

## Important Notes

- **Approved enterprise agreements:** Amdocs holds enterprise license agreements (ELAs) with major vendors offering 15–40% discounts vs. list price. Always purchase through ELAs when available.
- **SaaS security requirements:** All SaaS products must support SSO (SAML/OIDC), encrypt data at rest (AES-256), and provide data export/deletion capabilities.
- **Shadow IT prohibition:** Purchasing software on personal credit cards or expensing without SAM approval violates Amdocs policy (KB-SEC-007).
- **Cloud services (AWS, Azure, GCP):** Procure through FinOps (`finops@amdocs.com`) using pre-approved organizational accounts only.

## Contact Information

- **Software Asset Management:** sam@amdocs.com
- **Software Procurement:** software-procurement@amdocs.com
- **Enterprise Architecture:** ea@amdocs.com
- **Procurement Team:** procurement@amdocs.com
- **FinOps (cloud services):** finops@amdocs.com
