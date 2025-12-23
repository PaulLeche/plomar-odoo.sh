# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductUomCategoryFel(models.Model):
    _name = 'sv_fe.uom.fel'
    _description = 'uom fel'
    _rec_name = 'name_uom'

    code = fields.Char()
    name_uom = fields.Char()
    product_ids = fields.One2many('product.template', 'sv_fe_unidad_medida_id', string='Code Fel')

