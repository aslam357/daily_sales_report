from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_paid = fields.Boolean(
        compute='_compute_is_paid', 
        store=True
    )

    delivery_status = fields.Selection(
        compute='_compute_delivery_status',
        selection=[
            ('not_delivered', 'Not Delivered'),
            ('partially_delivered', 'Partially Delivered'),
            ('fully_delivered', 'Fully Delivered')
        ],
        store=True,
        string='Delivery Status'
    )

    @api.depends('invoice_ids.payment_state')
    def _compute_is_paid(self):
        for order in self:
            order.is_paid = all(invoice.payment_state == 'paid' for invoice in order.invoice_ids)

    @api.depends('picking_ids.state')
    def _compute_delivery_status(self):
        for order in self:
            if all(picking.state == 'done' for picking in order.picking_ids):
                order.delivery_status = 'fully_delivered'
            elif any(picking.state == 'done' for picking in order.picking_ids):
                order.delivery_status = 'partially_delivered'
            else:
                order.delivery_status = 'not_delivered'
