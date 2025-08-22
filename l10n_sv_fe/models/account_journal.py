# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
import logging

_logger = logging.getLogger(__name__)

SV_FE_TYPE_DTE = [
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

    sv_fe_type = fields.Selection(SV_FE_TYPE_DTE, string='Tipo DTE')
    sv_fe_establishment_id = fields.Many2one('sv_fe.res.company.establishment', string='Establecimiento')
    sv_fe_active = fields.Boolean(string="FE Activo")
    sv_fe_country_code = fields.Char(related='company_id.country_code', string='Country Code', store=True, readonly=True)