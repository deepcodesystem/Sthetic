# -*- coding: utf-8 -*-
from odoo import models


class SaleDeliveredReport(models.AbstractModel):
    """Parser du rapport 'Bon de commande (Qté livrée)'.

    Recalcule, pour chaque ligne de commande, le sous-total HT, le montant
    de taxes et le total TTC en se basant sur qty_delivered au lieu de
    product_uom_qty. Les lignes non livrées (qty_delivered = 0) ainsi que
    les lignes de type section/note sont ignorées.
    """

    _name = 'report.sale_delivered_report.report_saleorder_delivered'
    _description = 'Rapport - Bon de commande (Quantités livrées)'

    def _compute_line_values(self, line):
        qty = line.qty_delivered
        price_unit = line.price_unit
        discount = line.discount or 0.0

        price_after_discount = price_unit * (1 - discount / 100.0)

        taxes_res = line.tax_id.compute_all(
            price_after_discount,
            currency=line.order_id.currency_id,
            quantity=qty,
            product=line.product_id,
            partner=line.order_id.partner_shipping_id or line.order_id.partner_id,
        )

        return {
            'line': line,
            'name': line.name,
            'qty_delivered': qty,
            'uom_name': line.product_uom.name if line.product_uom else '',
            'price_unit': price_unit,
            'discount': discount,
            'tax_names': ', '.join(t.invoice_label or t.name for t in line.tax_id),
            'price_subtotal': taxes_res['total_excluded'],
            'price_total': taxes_res['total_included'],
        }

    def _get_report_values(self, docids, data=None):
        orders = self.env['sale.order'].browse(docids)
        lines_data = {}
        totals_data = {}

        for order in orders:
            lines_vals = []
            amount_untaxed = 0.0
            amount_total = 0.0

            deliverable_lines = order.order_line.filtered(
                lambda l: not l.display_type and l.qty_delivered > 0
            )

            for line in deliverable_lines:
                vals = self._compute_line_values(line)
                lines_vals.append(vals)
                amount_untaxed += vals['price_subtotal']
                amount_total += vals['price_total']

            lines_data[order.id] = lines_vals
            totals_data[order.id] = {
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_total - amount_untaxed,
                'amount_total': amount_total,
            }

        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': orders,
            'lines_data': lines_data,
            'totals_data': totals_data,
        }
