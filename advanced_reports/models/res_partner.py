# -*- coding: utf-8 -*-
import re
from odoo import _, api, fields, models
from odoo.exceptions import UserError



class ResPartner(models.Model):
    _inherit = 'res.partner'

    taxpayer_type = fields.Selection([('little', 'Pequeño'),
                                      ('big', 'Grande'),
                                      ('medium', 'Mediano'),
                                      ('other', 'Otro')
                                      ], string="Tipo de contribuyente")
    vat = fields.Char(size=14, help="El número de identificación fiscal. Los valores establecidos aqui se validarán según el formato: 14 carácteres-sin guiones.")
    dui_field = fields.Char(size=9, help="Los valores establecidos aqui se validarán según el formato: 9 carácteres-sin guiones.")

    @api.constrains('dui_field')
    def _constraint_dui_field(self):
        for record in self:
            if record.dui_field:
                if not re.fullmatch(r'^[A-Za-z0-9]{9}$', record.dui_field):
                    raise UserError("DUI debe tener un largo de 9 carácteres \nsin guiones")

    @api.constrains('vat')
    def _constraint_vat(self):
        for record in self:
            if record.vat:
                if not re.fullmatch(r'^[A-Za-z0-9]{14}$', record.vat):
                    raise UserError("NIT debe tener un largo de 14 carácteres \nsin guiones")



    @api.depends('is_consumer_taxp')
    def _compute_type_consumer_taxp(self):
        for partner in self:
            partner.type_consumer_taxp = 'consumer' if partner.is_consumer_taxp else 'taxpayer'

    type_consumer_taxp = fields.Selection(string='Tipo consumidor',
                                          selection=[('taxpayer', 'Contribuyente'), ('consumer', 'Consumidor final')],
                                          compute='_compute_type_consumer_taxp', inverse='_write_type_consumer_taxp')

    is_consumer_taxp = fields.Boolean(string="Es Consumidor final", default=False)

    def _write_type_consumer_taxp(self):
        for partner in self:
            partner.is_consumer_taxp = partner.type_consumer_taxp == 'consumer'

    @api.onchange('type_consumer_taxp')
    def onchange_type_consumer_taxp(self):
        self.is_consumer_taxp = (self.type_consumer_taxp == 'consumer')


    house_number = fields.Char(string="No. Casa")
    local_apartment = fields.Char(string="Apart./Local")
    address_information = fields.Char(string="Otros Datos Domicilio")


