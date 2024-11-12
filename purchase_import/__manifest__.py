# -*- coding: utf-8 -*-


{
    'name': "Commerce Extérieur",
    'author': 'Finoutsource',
    'category': 'purchase',
    'summary': """Importation app by miza""",
    'license': 'AGPL-3',
    'website': '',
    'description': """
""",
    'version': '17.0.0.1',
    'depends': ["purchase", 'stock','base','credit_bancaire'],
    'data': [
    'security/purchase_import_role.xml',
    'data/import_stage_data.xml',
    'data/ir_cron.xml',
    'views/import_folder_view.xml',
    'views/inherits_view.xml',
    'views/sequence.xml',
    'views/purchase_international.xml',
    'views/d10_products_view.xml',
    'views/model_dossier_view.xml',
    'views/supplier_receipt.xml',
    'views/d10_view.xml',
    'security/ir.model.access.csv',

    ],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
