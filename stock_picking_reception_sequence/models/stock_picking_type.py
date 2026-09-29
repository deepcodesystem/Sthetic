# -*- coding: utf-8 -*-
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    use_return_sequence = fields.Boolean(
        string='Utiliser la sequence des retours',
        default=True,
        help="Si cette option est cochee, les receptions generees comme retour d'un "
             "transfert seront numerotees avec la sequence dediee aux retours "
             "(prefixe par defaut : RET/) au lieu de la sequence de l'operation type.")
