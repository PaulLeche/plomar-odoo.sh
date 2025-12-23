# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AddressDepartamento(models.Model):
    _name = 'sv_fe.address.depart.fel'
    _description = 'address depart fel'
    _rec_name = 'name_depart'

    code = fields.Char()
    name_depart = fields.Char()
    partner_ids = fields.One2many('res.partner', 'sv_fe_address_dep', string='Departamento')


class AddressMunicipio(models.Model):
    _name = 'sv_fe.address.muni.fel'
    _description = 'address muni fel'
    _rec_name = 'name_muni'

    code_muni = fields.Char()
    code_dep  = fields.Char()
    name_muni = fields.Char()

    partner_ids = fields.One2many('res.partner', 'sv_fe_address_mun', string='Departamento')


class ExportCountry(models.Model):
    _name = 'sv_fe.export.country'
    _description = 'export country'
    _rec_name = 'name_country'

    code_country = fields.Char()
    name_country = fields.Char()

    partner_ids = fields.One2many('res.partner', 'sv_fe_country', string='Departamento')

