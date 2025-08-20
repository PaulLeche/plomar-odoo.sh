# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    sv_fe_user = fields.Char(string='Usuario')
    sv_fe_key_webservice = fields.Char(string='Llave')
    sv_fe_sign_token = fields.Char(string='Sign Token')
    sv_fe_other_email = fields.Char(string="Otro Email")
    sv_fe_establishment_ids = fields.One2many('sv_fe.res.company.establishment', 'company_id', string='Establecimientos')
    sv_fe_mode_prod = fields.Boolean(string='Prod Mode')
    sv_fe_url_prod = fields.Char(string='URL Prod')
    sv_fe_url_test = fields.Char(string='URL Test')
    country_code = fields.Char(related='country_id.code', string='Country Code', store=True, readonly=True)

    def sv_fe_get_fe_url(self):
        return self.sv_fe_url_prod if self.sv_fe_mode_prod else self.sv_fe_url_test

    def sv_fe_get_headers(self):
        headers = {'Content-Type': 'application/json'}
        if not self.sv_fe_user and not self.sv_fe_key_webservice:
            raise ValidationError(_("Error. credentials aren't setted"))
        headers.update( {'usuario': self.sv_fe_user, 'llave': self.sv_fe_key_webservice} )
        return headers

    def sv_fe_get_sign_token(self):
        if not self.sv_fe_sign_token:
            raise ValidationError(_("Error. Token isn't setted"))
        return {
            "llave": self.sv_fe_sign_token,
            "alias": self.sv_fe_user
        }


class ResCompanyEstablishment(models.Model):
    _name = 'sv_fe.res.company.establishment'
    _description = 'Company Establishment'
    _rec_name = 'fe_tradename'

    fe_tradename = fields.Char(string='Nombre Comercial', required=True)
    fe_code = fields.Char(string="Código establecimiento", required=True)
    company_id = fields.Many2one('res.company', string='Compañia')
    export_code = fields.Char(string='Código exportación')
    