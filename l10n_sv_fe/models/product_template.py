# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

SV_FE_TYPE_SERVICE = [
    ('01', 'Bienes'),
    ('02', 'Servicios'),
    ('03', 'Ambos'),
    ('04', 'Otros'),
]


class PaymentMethodFel(models.Model):
    _inherit = 'product.template'

    sv_fe_services = fields.Selection(SV_FE_TYPE_SERVICE, string='Tipo Servicio', store=True)
    sv_fe_unidad_medida_id = fields.Many2one('sv_fe.uom.fel', string='Unidad de medida fel', store=True)
    sv_fe_tributes_id = fields.Many2one('sv_fe.tribute.fel', string='Tributo', store=True)
    sv_fe_product_country_code = fields.Char(string='Country Code', compute="_compute_country_code", store=False, readonly=True)

    @api.depends('company_id', 'company_id.country_id.code')
    @api.depends_context('company')
    def _compute_country_code(self):
        for record in self:
            record.sv_fe_product_country_code = self.env.company.country_id.code if self.env.company.country_id else ''
