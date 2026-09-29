# -*- coding: utf-8 -*-
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

RETURN_SEQUENCE_CODE = 'stock.picking.incoming.return'


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _return_sequence(self, picking_type):
        """Return the sequence used to number the returns of the given operation type."""
        sequences = self.env['ir.sequence'].sudo().search([('code', '=', RETURN_SEQUENCE_CODE)])
        sequence = sequences.filtered(lambda seq: seq.company_id == picking_type.company_id)
        sequence = sequence or sequences.filtered(lambda seq: not seq.company_id)
        if not sequence:
            _logger.warning(
                "Sequence '%s' introuvable : les receptions de type retour garderont "
                "la sequence de leur operation type.", RETURN_SEQUENCE_CODE)
        return sequence[:1]

    @api.model
    def _vals_are_return(self, vals):
        """Tell whether picking values describe a return of an existing transfer."""
        if vals.get('return_id'):
            return True
        commands = (vals.get('move_ids') or []) + (vals.get('move_ids_without_package') or [])
        for command in commands:
            if not isinstance(command, (list, tuple)) or len(command) < 3:
                continue
            values = command[2]
            if isinstance(values, dict) and values.get('origin_returned_move_id'):
                return True
        return False

    @api.model
    def _use_return_sequence(self, picking_type, vals):
        """Tell whether the given incoming picking values must use the return sequence."""
        if not picking_type or picking_type.code != 'incoming' or not picking_type.use_return_sequence:
            return False
        return self._vals_are_return(vals)

    @api.model
    def _get_reception_reference(self, picking_type, vals):
        if not self._use_return_sequence(picking_type, vals):
            return False
        sequence = self._return_sequence(picking_type)
        return sequence.next_by_id() if sequence else False

    @api.model_create_multi
    def create(self, vals_list):
        defaults = self.default_get(['name', 'picking_type_id'])
        for vals in vals_list:
            if vals.get('name', '/') != '/' or defaults.get('name', '/') != '/':
                continue
            picking_type = self.env['stock.picking.type'].browse(
                vals.get('picking_type_id') or defaults.get('picking_type_id'))
            reference = self._get_reception_reference(picking_type, vals)
            if reference:
                vals['name'] = reference
        return super().create(vals_list)

    def write(self, vals):
        references = {}
        if vals.get('picking_type_id'):
            picking_type = self.env['stock.picking.type'].browse(vals['picking_type_id'])
            for picking in self.filtered(lambda rec: rec.picking_type_id != picking_type):
                reference = self._get_reception_reference(picking_type, {
                    'return_id': picking.return_id.id,
                })
                if reference:
                    references[picking.id] = reference
        res = super().write(vals)
        for picking in self.browse(list(references)):
            picking.sudo().name = references[picking.id]
        return res
