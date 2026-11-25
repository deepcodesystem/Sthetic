{
    'name': 'Rapport des BL impayés',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': "Rapport PDF / Excel des bons de commande (BL) impayés, tous clients confondus",
    'description': """
Rapport des BL impayés
======================

Assistant (Ventes > Rapports > BL impayés) qui génère, en PDF ou en Excel,
la liste de tous les bons de commande confirmés (BL) dont le reste à payer
est positif, tous clients confondus. Une ligne = un BL, avec :

- N° BL, date, client, ville,
- montant TTC du BL, montant payé, reste à payer,
- totaux en bas du rapport.

Montant payé = somme des montants réglés sur les factures validées du BL,
moins les montants réglés sur ses avoirs.
Reste à payer = montant TTC du BL - avoirs validés - montant payé
(un BL non facturé est donc entièrement impayé).
    """,
    'author': 'DeepCode',
    'website': 'https://deeposapps.com',
    'depends': ['sale'],
    'external_dependencies': {'python': ['xlsxwriter']},
    'data': [
        'security/ir.model.access.csv',
        'report/unpaid_bl_report_actions.xml',
        'report/unpaid_bl_report_templates.xml',
        'wizard/unpaid_bl_report_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
