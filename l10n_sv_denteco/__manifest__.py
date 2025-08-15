# -*- coding: utf-8 -*-
{
    'name': "Gestión de Proyectos",

    'summary': "Desarrollo personalizado Para DENTECO, S.A.",

    'description': """
 Desarrollo personalizado Para DENTECO, S.A
    """,

    'author': "Nery Sinay",
    'website': "https://denteco.odoo.com",
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'helpdesk', 'calendar', 'base_address_extended'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/helpdesk_ticket_views.xml',
        'views/res_partner_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

