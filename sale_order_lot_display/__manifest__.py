{
    'name': 'Sale Order Lot Display',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Affiche les numéros de lot/série des livraisons dans les rapports devis/commande',
    'description': """
Module Sthetic - Affichage des Lots/Séries sur les Rapports de Vente
=====================================================================
Ajoute une colonne "Lot / Série" dans les rapports Devis et Commandes,
affichant les numéros de lot/série associés à chaque ligne (via les
mouvements de stock), que la livraison ait été effectuée ou non.
    """,
    'author': 'GetapERP',
    'website': 'https://www.getaperp.com',
    'depends': [
        'sale_management',
        'sale_stock',
        'stock',
    ],
    'data': [
        'views/sale_order_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
