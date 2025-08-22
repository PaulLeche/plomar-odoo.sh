# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

TYPE_FE = [
    ('FACT', 'Factura'),
    ('FCAM', 'Factura Cambiaria'),
    ('FPEQ', 'Factura Pequeño Contribuyente'),
    ('FCAP', 'Factura Cambiaria Pequeño Contribuyente'),
    ('FAEX', 'Factura de Exportación'),
    ('FESP', 'Factura Especial'),
    ('NABN', 'Nota de Abono'),
    ('RDON', 'Recibo por donación'),
    ('RECI', 'Recibo'),
    ('NDEB', 'Nota de Débito'),
    ('NCRE', 'Nota de Crédito'),
    ('FACA', 'Factura Contribuyente Agropecuario'),
    ('FCCA', 'Factura Cambiaria Contribuyente Agropecuario'),
    ('FAPE', 'Factura Pequeño Contribuyente Régimen Electrónico'),
    ('FCPE', 'Factura Cambiaria Pequeño Contribuyente Régimen Electrónico'),
    ('FAAE', 'Factura Contribuyente AgropecuarioRégimen Electrónico Especial'),
    ('FCAE', 'Factura Cambiaria Contribuyente AgropecuarioRégimen Electrónico Especial'),
]


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    fe_type = fields.Selection(TYPE_FE, string='Type')
    fe_establishment_id = fields.Many2one('res.company.establishment', string='Establishment')
    fe_active = fields.Boolean(string="Active FE")
    journal_country_code = fields.Char(related='company_id.country_code', string='Country Code', store=True, readonly=True)