# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"
    _description = "Journal Entry"

    uuid_user = fields.Char(string="UUID ", help="El campo UUID se validará según el formato: XXXXXXXX-XXXX--XXXX--XXXX-XXXXXXXXXXXX ")
    number_resolution = fields.Char(string="Número de resolucíon")
    number_of_series_document_supplier = fields.Char(string='Número de serie de documento (FEL)')

    document_number = fields.Char(string="Número de documento")
    date_payment = fields.Date(string="Fecha de pago")

    @api.constrains('uuid_user')
    def _check_uuid_user(self):
        for record in self:
            if record.uuid_user:
                if not re.fullmatch(r'^[A-Za-z0-9]{8}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{12}$', record.uuid_user):
                    raise UserError("Código de generación debe tener el formato: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX ")

    def action_post(self):
        if not (self.type_of_operation and self.document_classification and self.sector and self.type_of_cost_or_expense):
            if self.move_type == 'in_invoice':
                raise UserError("Los campos: Tipo de operación, Clasificación del documento, Sector, Tipo de costo o gasto. Deben ser obligatorios para confirmar la factura")
        res = super(AccountMove, self).action_post()
        return res


    aduana_code_id = fields.Many2one('aduana.code', string="Cod. Aduana")
    concept_operation = fields.Selection([
        ('import', '[1]Importación'),
        ('internment', '[2]Internación'),
        ('services', '[3]Importación de servicios')
    ], string="Concepto de Operación")

    import_type = fields.Selection([
        ('statement', '[1]Declaración de Mercancía'),
        ('form', '[2]Formulario Aduanero'),
        ('fyduca', '[3]FYDUCA'),
        ('other', '[4]Otro'),
    ], string="Tipo Doc. Importación")


    @api.depends('partner_id', 'partner_id.name')
    def _compute_partner_country(self):
        for record in self:
            partner_country = ''
            if record.partner_id and record.partner_id.country_id and record.partner_id.country_id.name:
                partner_country = record.partner_id.country_id.name
            record.partner_country = partner_country

    partner_country = fields.Char(string="País", compute='_compute_partner_country')

    type_rental_operation = fields.Selection([
        ('1', '[1] Gravada'),
        ('2', '[2] No Gravada'),
        ('3', '[3] Excluido o no constituye renta'),
        ('4', '[4] Mixta (Se refiere cuando en un mismo documento se encuentre una operación gravada y exenta.)'),
        ('12', '[12] Ingresos que ya fueron sujetos de retención informados en el F14 y consolidados en F910'),
        ('13', '[13] Sujetos pasivos excluidos (art. 6 LISR) e ingresos que no constituyen hecho generador del ISR'),
    ], string="Tipo de Operación (Renta)")

    type_rental_income = fields.Selection([
        ('1', '[1] Profesiones, Artes y Oficios'),
        ('2', '[2] Actividades de Servicios'),
        ('3', '[3] Actividades Comerciales'),
        ('4', '[4] Actividades Industriales'),
        ('5', '[5] Actividades Agropecuarias'),
        ('6', '[6] Utilidades y Dividendos'),
        ('7', '[7] Exportaciones de bienes'),
        ('8', '[8] Servicios Realizados en el Exterior y Utilizados en El Salvador'),
        ('9', '[9] Exportaciones de servicios'),
        ('10', '[10] Otras Rentas Gravables'),
        ('12', '[12] Ingresos que ya fueron sujetos de retención informados en el F14 y consolidados en F910'),
        ('13', '[13] Sujetos pasivos excluidos (art. 6 LISR) e ingresos que no constituyen hecho generador del ISR'),
    ], string="Tipo de Ingreso (Renta)")

    type_of_operation = fields.Selection(selection_add=[('4', '[4]Mixta')])

