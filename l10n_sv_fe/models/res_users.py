# -*- coding: utf-8 -*-

from odoo import models, fields

TYPE_IDENTIFICATION = [
    ('36', 'NIT'),
    ('13', 'DUI'),
    ('37', 'Otro'),
    ('03', 'Pasaporte'),
    ('02', 'Carnet de Residente')
]


class ResUsers(models.Model):
    _inherit = 'res.users'

    fe_establishment_id = fields.Many2one('res.company.establishment', string='Establecimiento')
    identification_type = fields.Selection(TYPE_IDENTIFICATION, string="Tipo de identificación", default='36', store=True)

    dui_field = fields.Char(string="DUI", store=True)
    other_field = fields.Char(string="Otro", store=True)
    passport_field = fields.Char(string="Pasaporte", store=True)
    carnet_residente_field = fields.Char(string="Carnét de Residente", store=True)
