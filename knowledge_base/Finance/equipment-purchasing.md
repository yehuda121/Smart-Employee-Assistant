# Equipment Purchasing

## Purpose

This document describes the procedure for purchasing equipment at Amdocs, covering IT hardware, office equipment, lab equipment, and other physical assets. Standardized purchasing ensures budget control, vendor compliance, asset tracking, and warranty management.

## Scope

This procedure applies to all equipment purchases exceeding $500 USD (or local equivalent). Purchases under $500 may use the corporate credit card (KB-FIN-003) or departmental petty cash. IT laptop purchases follow KB-IT-004 regardless of amount.

## Procedure

1. **Identify the need and specifications.** Document the equipment required: type, specifications, quantity, and business justification. Check if the item is available through existing Amdocs contracts (see Approved Vendor List at `https://procurement.amdocs.internal/vendors`).

2. **Verify budget availability.** Confirm funds in your department cost center (CC-XXXX-DEPT) via the FinOps dashboard (`https://finops.amdocs.internal`). Purchases over $5,000 require a valid project code (PRJ-XXXX) with allocated budget.

3. **Select the purchasing path based on amount:**

   | Amount (USD) | Method | Approval Required |
   |---|---|---|
   | Under $500 | Corporate card or petty cash | Manager |
   | $500–$5,000 | Purchase requisition in SAP Ariba | Manager → Budget owner |
   | $5,000–$50,000 | Purchase requisition + 3 quotes | Manager → Director → Procurement |
   | Over $50,000 | Formal RFP process | VP → Procurement → Legal |

4. **Create a purchase requisition in SAP Ariba.** Log in to `https://ariba.amdocs.com` via Okta SSO. Navigate to **Create > Requisition**. Enter item details, preferred vendor (from Approved Vendor List), delivery location, cost center, and project code.

5. **Attach supporting documents.** Include: business justification, specification sheet, vendor quote(s), and manager approval email (if not routed through Ariba workflow).

6. **Procurement review.** The Procurement team reviews requisitions within 2 business days. They may negotiate pricing, suggest alternative vendors, or request additional quotes.

7. **Purchase order issuance.** Approved requisitions convert to Purchase Orders (POs) automatically (KB-FIN-009). The PO number is sent to the vendor and the requester. Expected delivery date is confirmed by the vendor.

8. **Receive and inspect equipment.** Upon delivery, verify the item matches the PO (model, quantity, condition). Confirm receipt in Ariba (**Receive > Confirm Receipt**). Report discrepancies or damage to Procurement within 48 hours.

9. **Asset registration.** IT equipment is auto-registered in the CMDB upon receipt. Non-IT equipment: Facilities registers assets over $1,000 in the Asset Management system. Affix the Amdocs asset tag when provided.

## Important Notes

- Capital vs. expense threshold: items over $5,000 with useful life exceeding 1 year are capitalized and depreciated over 3–5 years.
- Preferred vendors: Dell (IT hardware), CDW (peripherals), Steelcase (furniture). Off-list vendors require Procurement exception approval.
- International purchases may require import duties and extended lead times. Contact Procurement for cross-border orders.
- Equipment warranties are tracked centrally. Do not purchase extended warranties — Amdocs self-insures equipment under $10,000.
- Donated or free equipment from vendors must still be registered and may require Legal review for compliance implications.

## Contact Information

- **Procurement Team:** procurement@amdocs.com
- **SAP Ariba Portal:** `https://ariba.amdocs.com`
- **FinOps Dashboard:** `https://finops.amdocs.internal`
- **Finance Helpdesk:** finance-help@amdocs.com | Internal ext. 5200
