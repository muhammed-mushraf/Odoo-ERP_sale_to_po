from odoo import models, fields, api


class SaleInherit(models.Model):
    _inherit = 'sale.order'
    order_count = fields.Integer(string='Count', compute='get_order_count')

    @api.model
    def action_confirm(self):
        res = super(SaleInherit, self).action_confirm()
        for order_line in self:
            for j in order_line.order_line:
                for move in j.move_ids:
                    move.write({'inventory_sn': j.sale_sn})
        return res

    def get_order_count(self):
        for rec in self:
            rec.order_count = self.env['purchase.order'].search_count([('sale_order_id', '=', self.id)])

    def button_custom(self):
        # Get the current sale order lines
        sale_order_lines = self.order_line.filtered(lambda line: line.product_id)

        # Create a list of dictionaries to pass the data to the vendor.new form view
        vendor_order_lines = []
        for line in sale_order_lines:
            vendor_order_lines.append((0, 0, {
                'p': line.product_id.id,
                'd': line.name,
                'q': line.product_uom_qty,
                'u': line.price_unit,
                's': line.price_subtotal,
                'sale_order_line_id': line.id,
            }))

        print("Vendor Order Lines:", vendor_order_lines)

        return {
            'name': 'Vendor Form',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'vendor.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_vendors_ids': vendor_order_lines,
                'default_sale_order_id': self.id,
            },
        }

    def vendor_rec(self):
        # Filter purchase orders related to the current sale order
        purchase_orders = self.env['purchase.order'].search([('sale_order_id', '=', self.id)])

        return {
            'name': 'Purchase Orders',
            'view_type': 'tree',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('id', 'in', purchase_orders.ids)],  # Filter based on sale order
        }


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order')


class Vendor(models.TransientModel):
    _name = 'vendor.wizard'

    name = fields.Many2one('res.partner', string='Vendor')
    selected_all = fields.Boolean(string='Select All', default=False)

    vendors_ids = fields.One2many('vendor.order', 'vendor_id', string='Sale Order Lines')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')

    @api.onchange('selected_all')
    def all_select(self):
        if self.selected_all:
            for i in self.vendors_ids:
                i.is_selected = True
        else:
            for i in self.vendors_ids:
                i.is_selected = False

    def to_quot(self):
        new_purchase_order = self.env['purchase.order'].create({
            'partner_id': self.name.id,
            'sale_order_id': self.sale_order_id.id,
        })

        selected_vendor_orders = self.vendors_ids.filtered(lambda x: x.is_selected)
        for i in selected_vendor_orders:
            purchase_order_line_vals = {
                'order_id': new_purchase_order.id,
                'product_id': i.p.id,
                'name': i.d,
                'product_qty': i.q,
                'price_unit': i.u,
                'sale_line_id': i.sale_order_line_id.id,
            }
            print("Sale Order Line ID:", i.sale_order_line_id.id)
            print(self.sale_order_id.id)
            print("Purchase Order Lines:", purchase_order_line_vals)
            new_purchase_order_line = self.env['purchase.order.line'].create(purchase_order_line_vals)

            sale_order_line = i.sale_order_line_id
            sale_order_line_vals = {
                'sale_sequence': new_purchase_order_line.purchase_sequence,
                'x_field': 'approved',
            }
            sale_order_line.write(sale_order_line_vals)
        not_selected_vendor_orders = self.vendors_ids.filtered(lambda x: not x.is_selected)
        for j in not_selected_vendor_orders:
            sale_order_lines = j.sale_order_line_id
            sale_order_line_vals = {
                'x_field': 'not_approved',
            }
            sale_order_lines.write(sale_order_line_vals)
        return


class SaleOrderLine(models.TransientModel):
    _name = 'vendor.order'

    vendor_id = fields.Many2one('vendor.wizard', string='Vendor')
    p = fields.Many2one('product.product', string='Product')
    d = fields.Char(string="Description")
    q = fields.Integer(string='QTY')
    seq = fields.Char(string='Sequence')
    u = fields.Integer(string='Unit Price')
    s = fields.Integer(string='Sub Total')
    is_selected = fields.Boolean(string='Is Selected', default=False)
    sale_order_line_id = fields.Many2one('sale.order.line', string="Sale Order Line")


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order.line'

    x_field = fields.Selection([('approved', 'Approved'), ('not_approved', 'Not Approved')], string="Stat", default="")
    sale_sequence = fields.Char(string="Sequence")
    sale_sn = fields.Integer(string='S.N')
    amount = fields.Monetary(string="Amount")

    @api.onchange('amount')
    def onchange_amount(self):
        if self.amount:
            self.discount = (self.amount / (self.price_unit * self.product_uom_qty)) * 100.0 if (
                    self.price_unit * self.product_uom_qty) else 0.0


class Inventory(models.Model):
    _inherit = 'stock.move'

    inventory_sn = fields.Integer(string='S.N')


class InventoryPicking(models.Model):
    _inherit = 'stock.picking'

    inventory_sn = fields.Integer(string='S.N')


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    purchase_sequence = fields.Char(string="Sequence")
    sale_line_id = fields.Many2one('sale.order.line', string="Sale Order Line")

    @api.model
    def create(self, vals):
        vals['purchase_sequence'] = self.env['ir.sequence'].next_by_code('purchase.order.line.sequence')
        result = super(PurchaseOrderLine, self).create(vals)
        return result
