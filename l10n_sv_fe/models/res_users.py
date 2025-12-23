# -*- coding: utf-8 -*-

from odoo import models, fields

SV_FE_TYPE_IDENTIFICATION = [
    ('36', 'NIT'),
    ('13', 'DUI'),
    ('37', 'Otro'),
    ('03', 'Pasaporte'),
    ('02', 'Carnet de Residente')
]


class ResUsers(models.Model):
    _inherit = 'res.users'

    sv_fe_establishment_id = fields.Many2one('sv_fe.res.company.establishment', string='Establecimiento')
    sv_fe_identification_type = fields.Selection(SV_FE_TYPE_IDENTIFICATION, string="Tipo de identificación", default='36', store=True)

    sv_fe_dui_field = fields.Char(string="DUI", store=True)
    sv_fe_other_field = fields.Char(string="Otro", store=True)
    sv_fe_passport_field = fields.Char(string="Pasaporte", store=True)
    sv_fe_carnet_residente_field = fields.Char(string="Carnét de Residente", store=True)
    sv_fe_user_country_code = fields.Char(related='company_id.partner_id.country_id.code', string='Country Code', store=True, readonly=True)
