# Purchase Order Process

## Purpose

This document describes the Amdocs Purchase Order (PO) lifecycle from requisition creation through payment. Purchase Orders provide contractual authorization for vendor purchases, enable three-way matching for accounts payable, and ensure spending stays within approved budgets.

## Scope

This procedure applies to all Amdocs purchases requiring a formal PO, typically transactions exceeding $500 USD. POs are created in SAP Ariba and synced to SAP ERP for financial processing. Capital and operational purchases follow the same PO workflow with different GL account coding.

## Procedure

1. **Create a purchase requisition.** In SAP Ariba (`https://ariba.amdocs.com`), navigate to **Create > Requisition**. Enter:
   - Item description and catalog item (if available in Ariba catalog)
   - Quantity and unit price
   - Vendor (must be on Approved Vendor List — KB-FIN-005)
   - Cost center (CC-XXXX-DEPT) and GL account
   - Project code (PRJ-XXXX) if project-funded
   - Delivery location and required-by date
   - Justification (for non-catalog items)

2. **Route for approval.** Requisition approval follows amount-based routing (KB-FIN-004):
   - Under $5,000: manager → budget owner
   - $5,000–$50,000: manager → director → Procurement
   - Over $50,000: manager → director → VP → Procurement

3. **PO generation.** Upon final approval, Ariba automatically generates a PO with a unique number (format: PO-YYYY-NNNNNN). The PO is transmitted to the vendor via the Supplier Portal or email. The requester receives a PO confirmation notification.

4. **Vendor fulfillment.** The vendor acknowledges the PO and fulfills the order per the specified delivery date. For services, the vendor begins work upon PO issuance. Scope changes require a PO amendment (change order).

5. **Confirm receipt.** When goods are delivered or services are rendered, the requester confirms receipt in Ariba:
   - Navigate to **Receive > PO Lookup**
   - Enter PO number
   - Confirm quantity received and condition
   - For partial deliveries, confirm received quantities (remaining balance stays open)

6. **Invoice matching and payment.** The vendor submits an invoice (KB-FIN-007) referencing the PO number. AP performs three-way match (PO + Receipt + Invoice) and processes payment per vendor terms.

7. **Close the PO.** POs auto-close when fully received and invoiced. Open POs with no activity for 90 days are flagged for review. Requesters should close or cancel unused POs to release budget encumbrances.

8. **PO amendments and cancellations.** To modify a PO (quantity, price, scope), submit a change request in Ariba linked to the original PO. Amendments re-enter the approval workflow. Cancellations require requester and manager confirmation; vendor notification is automatic.

## Important Notes

- **Budget encumbrance:** PO approval reserves (encumbers) budget immediately. The encumbrance releases upon PO closure or cancellation.
- **Blanket POs:** Standing POs for recurring purchases (e.g., monthly SaaS subscriptions) are created by Procurement for approved vendors. Departments reference the blanket PO rather than creating individual requisitions.
- **Emergency POs:** For critical business needs, Procurement can issue an emergency PO with verbal VP approval, followed by formal approval within 48 hours.
- **PO vs. corporate card:** Use POs for vendor purchases over $500. Corporate card (KB-FIN-003) is for travel and expenses under $500.
- **Audit trail:** All PO transactions are logged in SAP with full approval history, retained for 7 years.

## Contact Information

- **SAP Ariba Portal:** `https://ariba.amdocs.com`
- **Procurement Team:** procurement@amdocs.com
- **Accounts Payable:** ap-invoices@amdocs.com
- **Finance Helpdesk:** finance-help@amdocs.com | Internal ext. 5200
