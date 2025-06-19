# -*- coding: utf-8 -*- 
{
    'name': 'Electronic Invoice GT',
    'version': '13.0',
    'license': "AGPL-3",
    'depends': [
        'account',
        'l10n_gt'
    ],
    'data': [
        'data/webservice_data.xml',
        'data/account_fe_phrase_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/company_views.xml',
        'views/account_move_views.xml',
        'views/account_journal_views.xml',
        'views/res_users_views.xml',
        'views/res_partner_view.xml',
    ]
}
