{
    'name': 'Sale Delivered Quantity Report',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': "Bon de commande basé sur les quantités livrées (après retour produit)",
    'description': """
Sale Delivered Quantity Report
===============================

Génère un document PDF similaire au devis / bon de commande standard, mais :
- remplace la quantité commandée (product_uom_qty) par la quantité livrée
  (qty_delivered) sur chaque ligne,
- recalcule le sous-total, les taxes et le total général en fonction de
  cette quantité livrée (et non de la quantité commandée initiale),
- n'affiche que les lignes réellement livrées.

Cas d'usage typique : après un retour partiel de marchandise de la part
du client, on souhaite fournir un document officiel reflétant ce qui a
réellement été livré (et donc facturable), différent du devis d'origine.
    """,
    'author': 'DeepCode',
    'website': 'https://deeposapps.com',
    'depends': ['sale_management', 'sale_stock', 'sale_order_lot_display'],
    'data': [
        'report/sale_delivered_report_actions.xml',
        'report/sale_delivered_report_templates.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
