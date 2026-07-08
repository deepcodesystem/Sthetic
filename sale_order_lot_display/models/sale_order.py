from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lot_ids_display = fields.Char(
        string='Lots/Séries/Quantités',
        compute='_compute_lot_ids_display',
    )

    @api.depends('move_ids.move_line_ids.lot_id', 'move_ids.move_line_ids.quantity')
    def _compute_lot_ids_display(self):
        for line in self:
            lot_qty = {}
            for ml in line.move_ids.move_line_ids:
                if ml.lot_id and ml.quantity:
                    lot_qty[ml.lot_id.name] = lot_qty.get(ml.lot_id.name, 0) + ml.quantity
            if lot_qty:
                parts = [f"{lot}: {qty:.2f}" for lot, qty in lot_qty.items()]
                line.lot_ids_display = ', '.join(parts)
            else:
                line.lot_ids_display = ''
