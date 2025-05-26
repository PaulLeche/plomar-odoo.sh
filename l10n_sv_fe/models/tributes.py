# -*- coding: utf-8 -*-

from odoo import fields, models, api


class TributesFel(models.Model):
    _name = 'tribute.fel'
    _rec_name = 'name_tribute'

    code = fields.Char()
    name_tribute = fields.Char()
    product_ids = fields.One2many('product.template', 'fe_tributes_id', string='Tributos')
