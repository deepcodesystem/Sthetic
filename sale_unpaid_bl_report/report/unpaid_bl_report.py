# -*- coding: utf-8 -*-
from odoo import models


class ReportUnpaidBl(models.AbstractModel):
    _name = 'report.sale_unpaid_bl_report.report_unpaid_bl'
    _description = 'Rapport - BL impayés'

    def _get_report_values(self, docids, data=None):
        wizards = self.env['unpaid.bl.report.wizard'].browse(docids)
        lines_data = {}
        totals_data = {}
        for wizard in wizards:
            lines = wizard._get_lines()
            lines_data[wizard.id] = lines
            totals_data[wizard.id] = wizard._get_totals(lines)
        return {
            'doc_ids': docids,
            'doc_model': 'unpaid.bl.report.wizard',
            'docs': wizards,
            'lines_data': lines_data,
            'totals_data': totals_data,
        }
