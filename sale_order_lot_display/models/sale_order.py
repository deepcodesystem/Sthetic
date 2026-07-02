from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lot_ids_display = fields.Char(
        string='Lots/Séries',
        compute='_compute_lot_ids_display',
    )

    @api.depends('move_ids.move_line_ids.lot_id')
    def _compute_lot_ids_display(self):
        for line in self:
            lots = line.move_ids.move_line_ids.lot_id.mapped('name')
            line.lot_ids_display = ', '.join(lots) if lots else ''
