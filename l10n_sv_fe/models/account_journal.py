# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
import logging

_logger = logging.getLogger(__name__)

TYPE_DTE = [
    ('01', 'Factura'),
    ('03', 'Comprobante de Crédito Fiscal'),
    ('04', 'Nota de Remisión'),
    ('05', 'Nota de Crédito'),
    ('06', 'Nota de Débito'),
    # ('07', 'Comprobante de Retención'),
    # ('08', 'Comprobante de Liquidación'),
    # ('09', 'Documento Contable de Liquidación'),
    ('11', 'Facturas de Exportación'),
    ('14', 'Factura de Sujeto Excluido'),
    # ('15', 'Comprobante de Donación'),
]


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    fe_type = fields.Selection(TYPE_DTE, string='Tipo DTE')
    fe_establishment_id = fields.Many2one('res.company.establishment', string='Establecimiento')
    fe_active = fields.Boolean(string="FE Activo")
