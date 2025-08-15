# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

TYPE_SERVICE = [
    ('01', 'Bienes'),
    ('02', 'Servicios'),
    ('03', 'Ambos'),
    ('04', 'Otros'),
]


class PaymentMethodFel(models.Model):
    _inherit = 'product.template'

    fe_services = fields.Selection(TYPE_SERVICE, string='Tipo Servicio', store=True)
    fe_unidad_medida_id = fields.Many2one('uom.fel', string='Unidad de medida fel', store=True)
    fe_tributes_id = fields.Many2one('tribute.fel', string='Tributo', store=True)
