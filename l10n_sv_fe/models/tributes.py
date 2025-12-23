# -*- coding: utf-8 -*-

from odoo import fields, models, api


class TributesFel(models.Model):
    _name = 'sv_fe.tribute.fel'
    _rec_name = 'name_tribute'

    code = fields.Char()
    name_tribute = fields.Char()
    product_ids = fields.One2many('product.template', 'sv_fe_tributes_id', string='Tributos')
