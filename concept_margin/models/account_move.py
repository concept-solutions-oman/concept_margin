from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    total_margin = fields.Monetary(string="Margin", compute='_compute_total_margin', store=True)
    margin_percent = fields.Float(string="Margin %", compute='_compute_total_margin', store=True)
    total_cost = fields.Monetary(string="Total Cost", compute='_compute_total_cost', store=True)
   

    @api.depends('invoice_line_ids.margin', 'amount_untaxed')
    def _compute_total_margin(self):
        for move in self:
            total_margin = sum(line.margin for line in move.invoice_line_ids if line.display_type == 'product')
            move.total_margin = total_margin
            move.margin_percent = (total_margin / move.amount_untaxed * 100.0) if move.amount_untaxed else 0.0

    @api.depends('invoice_line_ids.cost', 'invoice_line_ids.quantity')
    def _compute_total_cost(self):
        for move in self:
            move.total_cost = sum(
                (line.cost or 0.0) * (line.quantity or 0.0)
                for line in move.invoice_line_ids
                if line.display_type == 'product'
            )

    product_ids = fields.Many2many(
        'product.product',
        compute='_compute_product_ids',
        string='Products',
        store=False
    )

    def _compute_product_ids(self):
        for move in self:
            move.product_ids = move.invoice_line_ids.product_id


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    margin = fields.Monetary(string='Margin', compute='_compute_margin', store=True)
    cost = fields.Float(string="Cost")

    @api.depends('quantity', 'price_subtotal', 'product_id')
    def _compute_margin(self):
        for line in self:
            cost = line.product_id.standard_price or 0.0
            line.cost = cost
            line.margin = line.price_subtotal - (cost * line.quantity)


