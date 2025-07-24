# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    fe_user = fields.Char(string='Usuario')
    fe_key_webservice = fields.Char(string='Llave')
    fe_sign_token = fields.Char(string='Sign Token')
    fe_other_email = fields.Char(string="Otro Email")
    fe_establishment_ids = fields.One2many('res.company.establishment', 'company_id', string='Establecimientos')
    fe_mode_prod = fields.Boolean(string='Prod Mode')
    fe_url_prod = fields.Char(string='URL Prod')
    fe_url_test = fields.Char(string='URL Test')

    fel_enabled_sv = fields.Boolean(string='Enable FEL SV', compute='_compute_fel_enabled_sv', store=True, help="Automatically enabled for El Salvador companies.")

    @api.depends('country_id.code')
    def _compute_fel_enabled_sv(self):
        for record in self:
            record.fel_enabled_sv = record.country_id.code == 'SV'

    def _get_fe_url(self):
        return self.fe_url_prod if self.fe_mode_prod else self.fe_url_test

    def _get_headers(self):
        headers = {'Content-Type': 'application/json'}
        if not self.fe_user and not self.fe_key_webservice:
            raise ValidationError(_("Error. credentials aren't setted"))
        headers.update( {'usuario': self.fe_user, 'llave': self.fe_key_webservice} )
        return headers

    def _get_sign_token(self):
        if not self.fe_sign_token:
            raise ValidationError(_("Error. Token isn't setted"))
        return {
            "llave": self.fe_sign_token,
            "alias": self.fe_user
        }


class ResCompanyEstablishment(models.Model):
    _name = 'res.company.establishment'
    _description = 'Company Establishment'
    _rec_name = 'fe_tradename'

    fe_tradename = fields.Char(string='Nombre Comercial', required=True)
    fe_code = fields.Char(string="Código establecimiento", required=True)
    company_id = fields.Many2one('res.company', string='Compañia')
    export_code = fields.Char(string='Código exportación')
    