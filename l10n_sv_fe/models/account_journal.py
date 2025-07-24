# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
import logging

_logger = logging.getLogger(__name__)

TYPE_DTE_SV = [
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

    fe_type_sv = fields.Selection(TYPE_DTE_SV, string='Tipo DTE')
    fe_establishment_id = fields.Many2one('res.company.establishment', string='Establecimiento')
    fe_active_sv = fields.Boolean(string="FE Activo")
    fel_enabled_status_sv = fields.Boolean(string='FEL Habilitado', compute='_compute_fel_enabled_status_sv', store=True)

    @api.depends('company_id.fel_enabled_sv')
    def _compute_fel_enabled_status_sv(self):
        for record in self:
            record.fel_enabled_status_sv = record.company_id.fel_enabled_sv if record.company_id else False