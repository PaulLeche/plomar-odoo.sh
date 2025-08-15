# -*- coding: utf-8 -*- 

{
    'name': 'Custom account move',
    'version': '13.0',
    'license': "AGPL-3",
    'depends': [
        'account_accountant',
        'account',
        'sale'
    ],
    'data': [
        'views/account_move_form.xml'
    ],
    'installable': True,
    'auto_install': False,
}
