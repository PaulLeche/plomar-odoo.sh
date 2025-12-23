# -*- coding: utf-8 -*-

from odoo import fields, models, api


class CodigoActividad(models.Model):
    _name = 'sv_fe.codigoactividad.fel'
    _description = 'codigoactividad fel'
    _rec_name = 'activity_name'

    code = fields.Char()
    activity_name = fields.Char()
    partner_ids = fields.One2many('res.partner', 'sv_fe_code_activity', string='Actividad Económica', help='Este campo será necesario cuando se realize un ajuste en las facturas, es decír para crear un comprobante de crédito fiscal.')
