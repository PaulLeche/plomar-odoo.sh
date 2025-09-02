# -*- coding: utf-8 -*-

{
    'name': 'Reporteria el Salvador',
    'author': "Xetechs GT",
    'website': "http://www.xetechs.com",
    'support': '',
    'version': "18.0.1.0.0",
    'license': "LGPL-3",
    'depends': [
        'purchase',
        'account',
        'l10n_sv_fe',
    ],
    'data': ['views/purchase_order_view.xml',
             'views/account_move_view.xml',
             'views/pos_config_view.xml',
             'views/sale_order_view.xml',
    ]
}