# -*- coding: utf-8 -*-

from odoo import fields, models, api


class RecintoAdditament(models.Model):
    _name = 'sv_fe.export.recinto'
    _description = 'export recinto'
    _rec_name = 'name_recinto'

    code_recinto = fields.Char()
    name_recinto = fields.Char()
    account_move_ids = fields.One2many('account.move','sv_fe_recinto',string='Recinto Fiscal')


class RegimenAdditament(models.Model):
    _name = 'sv_fe.export.regimen'
    _description = 'export regimen'
    _rec_name = 'name_regimen'

    code_regimen = fields.Char()
    name_regimen = fields.Char()
    account_move_ids = fields.One2many('account.move', 'sv_fe_regimen', string='Régimen')


class IncotermAdditament(models.Model):
    _name = 'sv_fe.export.incoterm'
    _description = 'export incoterm'
    _rec_name = 'name_incoterm'

    code_incoterm = fields.Char()
    name_incoterm = fields.Char()
    account_move_ids = fields.One2many('account.move', 'sv_fe_incoterm', string='Código Incoterms')

