{
    'name': 'Sale Validation ICE Check',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Bloque la demande de validation tier si le client marocain n\'a pas de code ICE',
    'description': """
Sale Validation ICE Check
==========================

Bloque la demande de validation (tier validation) sur les commandes de vente
lorsque le client est marocain et ne dispose pas d'un code ICE renseigné.

- Affiche un bandeau d'avertissement sur le formulaire de la commande
- Lève une ValidationError si l'utilisateur tente de lancer la demande
- Ne concerne que les clients dont le pays est le Maroc (country_code = MA)
    """,
    'author': 'GetapERP',
    'website': 'https://www.getaperp.com',
    'depends': [
        'sale_tier_validation',
        'l10n_ma',
    ],
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
