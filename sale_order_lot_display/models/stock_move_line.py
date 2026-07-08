from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    sale_order_id = fields.Many2one(
        "sale.order",
        string="Sale Order",
        related="move_id.sale_line_id.order_id",
        store=True,
    )
