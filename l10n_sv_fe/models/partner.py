# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

TYPE_IDENTIFICATION = [
    ('36', 'NIT'),
    ('13', 'DUI'),
    ('37', 'Otro'),
    ('03', 'Pasaporte'),
    ('02', 'Carnet de Residente'),
]

TYPE_DTE_DEFAULT = [
    ('ccf', 'Comprobante de Crédito Fiscal'),
    ('fa', 'Factura'),
    ('facf', 'Factura de Consumidor Final'),
    ('faex', 'Factura de Exportación'),
]


class ResPartner(models.Model):
    _inherit = 'res.partner'

    identification_type = fields.Selection(TYPE_IDENTIFICATION, string="Tipo Identificación", default='36', store=True, required=True)
    fe_code_activity = fields.Many2one('codigoactividad.fel', string='Actividad Económica', store=True, help='La actividad económica será necesaria cuando se haga un ajuste.')
    fe_address_dep = fields.Many2one('address.depart.fel', string='Departamento', store=True, help='Será requerída cuando se cree una factura de exportación')

    fe_address_mun = fields.Many2one('address.muni.fel', string='Municipio', store=True, help='Será requerída cuando se cree una factura de exportación')
    fe_country = fields.Many2one('export.country', string='País Exportación', store=True, help='Será requerída cuando se cree una factura de exportación')
    complement_address = fields.Char(string='Dirección complementaria', help='Será requerída cuando se cree una factura de exportación')

    tipo_persona = fields.Selection([('1', 'Persona Natural'), ('2', 'Persona Jurídica')], string='Tipo de Persona', help="Este campo debe ser obligatorio cuando se genere una factura de exportación")
    movimiento_preferido_cliente = fields.Selection(TYPE_DTE_DEFAULT, string="Movimiento Preferido Cliente", store=True)
    dui_field = fields.Char(string="DUI", store=True)

    other_field = fields.Char(string="Otro", store=True)
    passport_field = fields.Char(string="Pasaporte", store=True)

    carnet_residente_field = fields.Char(string="Carnét de Residente", store=True)
    nrc = fields.Char(string="NRC", store=True)

    @api.constrains('nrc', 'identification_type', 'vat', 'dui_field')
    def _not_duplicate_nrc_nit_dui(self):
        for record in self:
            if record.nrc not in ['', False]:
                duplicate_nrc = self.search([('nrc', '=', record.nrc), ('id', '!=', record.id)], limit=1)
                if duplicate_nrc:
                    raise UserError('El contacto %s ya tiene el NRC: %s' % (duplicate_nrc.name, duplicate_nrc.nrc))
            if record.identification_type == '36' and record.vat not in ['', False]:
                duplicate_nit = self.search([('vat', '=', record.vat), ('id', '!=', record.id), ('identification_type', '=', '36')], limit=1)
                if duplicate_nit and record.company_type == 'company':
                    raise UserError('El contacto %s ya tiene el NIT: %s' % (duplicate_nit.name, duplicate_nit.vat))
            if record.identification_type == '13' and record.dui_field not in ['', False]:
                duplicate_dui = self.search([('dui_field', '=', record.dui_field), ('id', '!=', record.id), ('identification_type', '=', '13')], limit=1)
                if duplicate_dui:
                    raise UserError('El contacto %s ya tiene el DUI: %s' % (duplicate_dui.name, duplicate_dui.dui_field))

    @api.model
    def create(self, vals):
        if vals.get('company_type') == 'person' and vals.get('parent_id'):
            parent_partner = self.env['res.partner'].browse(vals.get('parent_id'))
            _logger.info("*********************************CONTACTO HIJOOOOOOOOOOOOOOO********************************")
            _logger.info(vals.get('parent_id'))
            _logger.info(parent_partner)
            if parent_partner and parent_partner.vat == vals.get('vat'):
                return super(ResPartner, self).create(vals)

        return super(ResPartner, self).create(vals)

    def _get_document_number(self):
        if self.identification_type == '36':
            return self.vat
        # DUI  
        if self.identification_type == '13':
            return self.dui_field[:-1] + '-' + self.dui_field[-1]
        # OTRO    
        if self.identification_type == '37':
            return self.other_field
        # PASAPORTE
        if self.identification_type == '03':
            return self.passport_field 
        # CARNET DE RESIDENTE
        if self.identification_type == '02':
            numero_documento = self.carnet_residente_field

        return None