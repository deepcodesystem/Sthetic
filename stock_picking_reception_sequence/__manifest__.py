# -*- coding: utf-8 -*-
{
    'name': 'Reception Picking Sequences',
    'version': '18.0.1.0.0',
    'category': 'Inventory',
    'summary': "Sequence dediee aux receptions de type retour, distincte des entrees fournisseurs.",
    'description': """
        Numerotation des receptions
        ===========================
        Ce module ajoute une seconde sequence pour les operations de type "Reception".

        - Les receptions fournisseurs (entrees achats) conservent la sequence standard
          de l'operation type (prefixe par defaut : WH/IN/).
        - Les receptions generees comme retour d'un transfert existant sont numerotees
          avec une sequence dediee (prefixe par defaut : RET/), ce qui permet de les
          distinguer immediatement des entrees fournisseurs.

        Le comportement peut etre desactive operation par operation type via le champ
        "Utiliser la sequence des retours".
    """,
    'author': 'GetapPRO',
    'website': 'https://www.getap.pro',
    'depends': ['stock'],
    'data': [
        'data/ir_sequence_data.xml',
        'views/stock_picking_type_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
