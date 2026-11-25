# -*- coding: utf-8 -*-
import base64
import io

from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

try:
    import xlsxwriter
except ImportError:  # pragma: no cover
    xlsxwriter = None


class UnpaidBlReportWizard(models.TransientModel):
    """Assistant du rapport 'BL impayés'.

    Un BL est un bon de commande (sale.order) confirmé. Pour chaque BL :
    - montant payé  = réglé sur ses factures validées - réglé sur ses avoirs
    - reste à payer = total TTC - avoirs validés - montant payé
    Seuls les BL dont le reste à payer est strictement positif sont listés.
    """

    _name = 'unpaid.bl.report.wizard'
    _description = 'Assistant - Rapport des BL impayés'

    date_from = fields.Date(string='Du')
    date_to = fields.Date(string='Au')
    partner_ids = fields.Many2many(
        'res.partner',
        string='Clients',
        help="Laisser vide pour inclure tous les clients.",
    )
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company,
    )
    excel_file = fields.Binary(string='Fichier Excel', readonly=True, attachment=False)
    excel_filename = fields.Char(string='Nom du fichier', readonly=True)

    # ------------------------------------------------------------------
    # Données
    # ------------------------------------------------------------------
    def _get_order_domain(self):
        self.ensure_one()
        domain = [
            ('state', '=', 'sale'),
            ('company_id', '=', self.company_id.id),
        ]
        if self.date_from:
            domain.append(('date_order', '>=', fields.Datetime.to_datetime(self.date_from)))
        if self.date_to:
            # date_to incluse : on prend tout ce qui est avant le lendemain 00:00
            domain.append(('date_order', '<', fields.Datetime.add(
                fields.Datetime.to_datetime(self.date_to), days=1)))
        if self.partner_ids:
            domain.append(('partner_id', 'child_of', self.partner_ids.ids))
        return domain

    def _compute_order_amounts(self, order):
        invoices = order.invoice_ids.filtered(lambda m: m.state == 'posted')
        out_invoices = invoices.filtered(lambda m: m.move_type == 'out_invoice')
        out_refunds = invoices.filtered(lambda m: m.move_type == 'out_refund')

        paid = (
            sum(inv.amount_total - inv.amount_residual for inv in out_invoices)
            - sum(ref.amount_total - ref.amount_residual for ref in out_refunds)
        )
        refunded = sum(out_refunds.mapped('amount_total'))
        residual = order.amount_total - refunded - paid
        return {
            'amount_total': order.amount_total,
            'amount_paid': paid,
            'amount_residual': residual,
        }

    def _get_lines(self):
        """Retourne la liste des BL impayés (une entrée par BL), triée par date."""
        self.ensure_one()
        orders = self.env['sale.order'].search(
            self._get_order_domain(), order='date_order asc, name asc')
        lines = []
        for order in orders:
            amounts = self._compute_order_amounts(order)
            rounding = order.currency_id.rounding
            if float_compare(amounts['amount_residual'], 0.0, precision_rounding=rounding) <= 0:
                continue
            partner = order.partner_id
            city = order.partner_shipping_id.city or partner.city or ''
            date_local = fields.Datetime.context_timestamp(order, order.date_order).date()
            lines.append({
                'order': order,
                'name': order.name,
                'date': date_local,
                'partner': partner.display_name,
                'city': city,
                'currency': order.currency_id,
                **amounts,
            })
        return lines

    def _get_totals(self, lines):
        return {
            'amount_total': sum(l['amount_total'] for l in lines),
            'amount_paid': sum(l['amount_paid'] for l in lines),
            'amount_residual': sum(l['amount_residual'] for l in lines),
        }

    def _get_period_label(self):
        self.ensure_one()
        fmt = '%d/%m/%Y'
        if self.date_from and self.date_to:
            return _('Du %(from)s au %(to)s',
                     **{'from': self.date_from.strftime(fmt), 'to': self.date_to.strftime(fmt)})
        if self.date_from:
            return _('À partir du %s', self.date_from.strftime(fmt))
        if self.date_to:
            return _("Jusqu'au %s", self.date_to.strftime(fmt))
        return _('Toutes dates')

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _check_dates(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError(_("La date de début doit être antérieure à la date de fin."))

    def action_print_pdf(self):
        self.ensure_one()
        self._check_dates()
        return self.env.ref(
            'sale_unpaid_bl_report.action_report_unpaid_bl').report_action(self)

    def action_export_xlsx(self):
        self.ensure_one()
        self._check_dates()
        if xlsxwriter is None:
            raise UserError(_("La librairie Python 'xlsxwriter' n'est pas installée."))

        lines = self._get_lines()
        totals = self._get_totals(lines)
        currency = self.company_id.currency_id

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('BL impayés')

        num_fmt = '#,##0.00'
        f_title = workbook.add_format({'bold': True, 'font_size': 14})
        f_sub = workbook.add_format({'italic': True, 'font_color': '#555555'})
        f_head = workbook.add_format({
            'bold': True, 'bg_color': '#D9E1F2', 'border': 1,
            'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
        f_text = workbook.add_format({'border': 1})
        f_date = workbook.add_format({'border': 1, 'num_format': 'dd/mm/yyyy', 'align': 'center'})
        f_amount = workbook.add_format({'border': 1, 'num_format': num_fmt})
        f_total_lbl = workbook.add_format({'bold': True, 'border': 1, 'bg_color': '#F2F2F2'})
        f_total = workbook.add_format({
            'bold': True, 'border': 1, 'bg_color': '#F2F2F2', 'num_format': num_fmt})

        headers = [
            ('N° BL', 18), ('Date', 12), ('Client', 40), ('Ville', 20),
            ('Montant TTC (%s)' % currency.name, 18),
            ('Montant payé (%s)' % currency.name, 18),
            ('Reste à payer (%s)' % currency.name, 18),
        ]

        sheet.write(0, 0, 'BL impayés - %s' % self.company_id.name, f_title)
        sheet.write(1, 0, self._get_period_label(), f_sub)
        sheet.write(2, 0, 'Nombre de BL : %s' % len(lines), f_sub)

        head_row = 4
        for col, (label, width) in enumerate(headers):
            sheet.set_column(col, col, width)
            sheet.write(head_row, col, label, f_head)
        sheet.set_row(head_row, 30)

        row = head_row + 1
        for line in lines:
            sheet.write(row, 0, line['name'], f_text)
            sheet.write_datetime(row, 1, fields.Datetime.to_datetime(line['date']), f_date)
            sheet.write(row, 2, line['partner'], f_text)
            sheet.write(row, 3, line['city'], f_text)
            sheet.write_number(row, 4, line['amount_total'], f_amount)
            sheet.write_number(row, 5, line['amount_paid'], f_amount)
            sheet.write_number(row, 6, line['amount_residual'], f_amount)
            row += 1

        sheet.merge_range(row, 0, row, 3, 'TOTAL', f_total_lbl)
        sheet.write_number(row, 4, totals['amount_total'], f_total)
        sheet.write_number(row, 5, totals['amount_paid'], f_total)
        sheet.write_number(row, 6, totals['amount_residual'], f_total)

        sheet.freeze_panes(head_row + 1, 0)
        if lines:
            sheet.autofilter(head_row, 0, row - 1, len(headers) - 1)

        workbook.close()
        self.write({
            'excel_file': base64.b64encode(output.getvalue()),
            'excel_filename': 'BL_impayes_%s.xlsx' % fields.Date.context_today(self).strftime('%Y%m%d'),
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=%s&id=%s&field=excel_file'
                   '&filename_field=excel_filename&download=true' % (self._name, self.id),
            'target': 'self',
        }
