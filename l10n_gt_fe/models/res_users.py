# -*- coding: utf-8 -*-

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    fe_establishment_id = fields.Many2one('res.company.establishment', string='Establecimiento')
    user_country_code = fields.Char(related='company_id.country_code', string='Country Code', store=True, readonly=True)