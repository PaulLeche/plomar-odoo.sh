# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, Command


class PosConfig(models.Model):
    _inherit = 'pos.config'

    number_of_cash_register = fields.Integer(string="Nº de maquina registradora")