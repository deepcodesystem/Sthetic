# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.stock_picking_reception_sequence.models.stock_picking import RETURN_SEQUENCE_CODE


@tagged('post_install', '-at_install')
class TestReceptionSequence(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref('stock.warehouse0')
        cls.incoming_type = cls.warehouse.in_type_id
        cls.supplier_location = cls.env.ref('stock.stock_location_suppliers')
        cls.customer_location = cls.env.ref('stock.stock_location_customers')
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.return_sequence = cls.env['ir.sequence'].search(
            [('code', '=', RETURN_SEQUENCE_CODE)], limit=1)
        cls.product = cls.env['product.product'].create({
            'name': 'Product Test Reception Sequence',
            'is_storable': True,
            'uom_id': cls.env.ref('uom.product_uom_unit').id,
            'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
        })
        cls.incoming_return_type = cls.env['stock.picking.type'].create({
            'name': 'Retours fournisseurs',
            'code': 'incoming',
            'sequence_code': 'stock.picking.incoming.return.type',
            'warehouse_id': cls.warehouse.id,
            'default_location_src_id': cls.stock_location.id,
            'default_location_dest_id': cls.supplier_location.id,
        })

    def _create_picking(self, **overrides):
        vals = {
            'picking_type_id': self.incoming_type.id,
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
        }
        vals.update(overrides)
        return self.env['stock.picking'].create(vals)

    def _validate_picking(self, picking, location_id):
        self.env['stock.move'].create({
            'name': '/',
            'product_id': self.product.id,
            'product_uom_qty': 5.0,
            'product_uom': self.env.ref('uom.product_uom_unit').id,
            'location_id': location_id.id,
            'location_dest_id': picking.location_dest_id.id,
            'picking_id': picking.id,
        })
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids._set_quantity_done(5.0)
        picking.button_validate()

    def _return_picking(self, picking):
        wizard = self.env['stock.return.picking'].with_context(active_id=picking.id).create({
            'picking_id': picking.id,
        })
        return self.env['stock.picking'].browse(wizard.action_create_returns_all()['res_id'])

    def test_return_sequence_exists(self):
        self.assertTrue(self.return_sequence, "La sequence des retours doit exister")
        self.assertTrue(self.return_sequence.prefix, "La sequence des retours doit avoir un prefixe")

    def test_standard_receipt_keeps_picking_type_sequence(self):
        picking = self._create_picking()
        self.assertNotEqual(picking.name, '/')
        self.assertFalse(
            picking.name.startswith(self.return_sequence.prefix),
            "Une entree fournisseur ne doit pas utiliser la sequence des retours")

    def test_receipt_return_uses_return_sequence(self):
        self.incoming_type.return_picking_type_id = self.incoming_return_type
        receipt = self._create_picking()
        self._validate_picking(receipt, self.supplier_location)

        returned = self._return_picking(receipt)
        self.assertEqual(returned.return_id, receipt)
        self.assertEqual(returned.picking_type_id, self.incoming_return_type)
        self.assertTrue(
            returned.name.startswith(self.return_sequence.prefix),
            "Le retour d'une reception doit utiliser la sequence dediee, obtenu : %s" % returned.name)

    def test_customer_return_received_in_stock_uses_return_sequence(self):
        outgoing_type = self.warehouse.out_type_id
        delivery = self.env['stock.picking'].create({
            'picking_type_id': outgoing_type.id,
            'location_id': self.stock_location.id,
            'location_dest_id': self.customer_location.id,
        })
        self._validate_picking(delivery, self.stock_location)

        returned = self._return_picking(delivery)
        self.assertEqual(returned.picking_type_id, self.incoming_type)
        self.assertTrue(
            returned.name.startswith(self.return_sequence.prefix),
            "Un retour client recu en stock doit utiliser la sequence dediee, obtenu : %s" % returned.name)

    def test_return_moves_without_return_id_use_return_sequence(self):
        original = self._create_picking()
        original_move = self.env['stock.move'].create({
            'name': '/',
            'product_id': self.product.id,
            'product_uom_qty': 1.0,
            'product_uom': self.env.ref('uom.product_uom_unit').id,
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'picking_id': original.id,
        })
        returned = self._create_picking(
            move_ids=[(0, 0, {
                'name': '/',
                'product_id': self.product.id,
                'product_uom_qty': 1.0,
                'product_uom': self.env.ref('uom.product_uom_unit').id,
                'location_id': self.supplier_location.id,
                'location_dest_id': self.stock_location.id,
                'origin_returned_move_id': original_move.id,
            })],
        )
        self.assertTrue(
            returned.name.startswith(self.return_sequence.prefix),
            "Un retour avec moves lies doit utiliser la sequence dediee aux retours, obtenu : %s" % returned.name)

    def test_outgoing_return_keeps_picking_type_sequence(self):
        outgoing_type = self.warehouse.out_type_id
        delivered = self.env['stock.picking'].create({
            'picking_type_id': outgoing_type.id,
            'location_id': self.stock_location.id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
        })
        returned = self.env['stock.picking'].create({
            'picking_type_id': outgoing_type.id,
            'location_id': self.env.ref('stock.stock_location_customers').id,
            'location_dest_id': self.stock_location.id,
            'return_id': delivered.id,
        })
        self.assertFalse(returned.name.startswith(self.return_sequence.prefix))

    def test_disabled_option_falls_back_to_picking_type_sequence(self):
        self.incoming_type.use_return_sequence = False
        original = self._create_picking()
        returned = self._create_picking(
            return_id=original.id,
            origin='Return of %s' % original.name)
        self.assertFalse(
            returned.name.startswith(self.return_sequence.prefix),
            "L'option desactivee doit replonger sur la sequence de l'operation type")
