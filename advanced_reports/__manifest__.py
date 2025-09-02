# -*- coding: utf-8 -*-
{
    "name": "Reportes de contabilidad avanzados",
    "author": "Omar Flores - oflores@xetechs.com",
    "website": "https://www.xetechs.com",
    "category": "Account",
    "license": "LGPL-3",
    "version": "18.0.1.0.0",
    "description": """
        Este módulo incluye:
        - Reporte de libro mayor por fechas.
        - Reporte de cierre de caja en formatos XLS y PDF.
        - Reporte F-07 xls.
        - Reporte-Libro de ventas,compras el Salvador.
        - Reporte F-14 xls.
        - Reporte planilla F-910 xls.
        - Reporte planilla F-930 xls.
        - Reporte F-983 xls.
        - Reporte F-987 xls.
    """,
    "depends": [
        "account",
        "account_reports",
        "report_xlsx",
        "l10n_sv_fe",
        "l10n_sv_report",
        "hr",
        "product",
        "hr_payroll",
        "l10n_sv_fe"
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/box_number_demo.xml",
        "views/box_number_view.xml",
        "views/cashier_model_view.xml",
        "views/box_payment_method_view.xml",
        "wizard/wizard_close_box_view.xml",
        "wizard/wizard_close_box_commission_view.xml",
        "views/account_payment_view.xml",
        "wizard/account_payment_register_view.xml",
        "reports/report_main.xml",
        "reports/report_close_box.xml",
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'wizard/wizard_planilla_f07.xml',
        'wizard/wizard_report_book.xml',
        'reports/report_taxpayer.xml',
        'reports/report_consumer.xml',
        'reports/report_purchase.xml',
        'views/hr_employee.xml',
        'wizard/wizard_planilla_f14.xml',
        'wizard/wizard_planilla_f910_view.xml',
        'wizard/wizard_planilla_f930_view.xml',
        'views/product_template_view.xml',
        'views/product_product_view.xml',
        'wizard/wizard_planilla_f983.xml',
        'data/aduana_code_demo.xml',
        'views/aduana_code_view.xml',
        'wizard/wizard_planilla_f987.xml',

    ],
    "auto_install": False,
    "installable": True,
}