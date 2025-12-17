# -*- coding: utf-8 -*- 

{
    'name': 'Electronic Invoice SV.',
    'author': "Xetechs GT",
    'website': "http://www.xetechs.com",
    'support': 'Jonathan Quintero --> jquintero@xetechs.com / Jorge Barrientos',
    'version': "16.0.1",
    'license': "LGPL-3",
    'depends': [
        'base',
        'uom',
        'account',
        'stock',
        'l10n_gt',
        #'sync_pos_fix_discount'
    ],
    'data': [
        'data/webservice_data.xml',
        'data/product_category_uom_fel_data.xml',
        'data/code_activity_fel_data.xml',
        'data/address_fel.xml',
        'data/tributes_data.xml',
        'data/country_data.xml',
        'data/recinto_additament_data.xml',
        'data/regimen_additament_data.xml',
        'data/incoterms_additament_data.xml',
        'data/impuestos.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/company_views.xml',
        'views/account_move_views.xml',
        'views/account_journal_views.xml',
        'views/res_users_views.xml',
        'views/res_partner_views.xml',
        'views/product_template_type_service_view.xml',
        'views/category_fel_product.xml',
        'views/code_activity_fel_view.xml',
        'views/stock_picking_views.xml',
        'report/invoice_fel_template.xml',
        'report/action_report.xml',
    ]
}
