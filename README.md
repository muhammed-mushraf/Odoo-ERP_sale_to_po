Sales and Purchase Order Integration.
This module extends the default sale.order and purchase.order models to integrate and streamline the workflow between sales and purchase orders. The functionality includes selecting vendors for sale order lines and creating corresponding purchase orders with specific sequences. Additionally, it provides an interface to view related purchase orders for a sale order.

Add Vendors and Select All Toggle in Sale Order Line Form.
When viewing a sale order, a custom button (button_custom) opens a form view (wizard) with the current sale order lines.
This form includes fields to select vendors for each sale order line and a toggle to select all lines.

Creating Purchase Orders from Selected Sale Order Lines.
Users can select preferred sale order lines using checkboxes.
Clicking the to_quot button will create a new purchase order for the selected lines.
Each purchase order line will have a sequence number generated and displayed in both sale.order.line and purchase.order.line.

Viewing Related Purchase Orders.
The vendor_rec function displays a tree view of all purchase orders created from the current sale order.
