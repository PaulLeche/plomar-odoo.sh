# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class AccountMove(models.Model):

    _inherit = "account.move"

    document_classification = fields.Selection([('1', '[1]Costo'),
                                                ('2', '[2]Gasto')],
                                               string='Clasificaciòn del documento')

    sector = fields.Selection([('1', '[1]Industria'),
                               ('2', '[2]Comercio'),
                               ('3', '[3]Agropecuaria'),
                               ('4', '[4]servicios, Profesiones, Arte y Oficios')],
                              string='Sector')

    type_of_cost_or_expense = fields.Selection([('1', '[1]Gasto de venta sin donacion'),
                                                ('2', '[2]Gasto de administracion sin donacion'),
                                                ('3', '[3]Gasto financiero sin donacion'),
                                                ('4',
                                                 '[4]Costos artículos producidos/comprados importaciones/internaciones'),
                                                ('5', '[5]Costos artículos producidos/comprados interno'),
                                                ('6', '[6]Costos indirectos de fabricación'),
                                                ('7', '[7]Mano de obra')],
                                               string='Tipo de costo o gasto')

    type_of_operation = fields.Selection([('1', '[1]Gravada'),
                                          ('2', '[2]No Gravada'),
                                          ('3', '[3]Excluido o no constituye renta')],
                                         string='Tipo de operacion')

    class_of_document = fields.Integer(string='Clase de documento', default=4)
    number_internal_control = fields.Char(string='Número de control interno')
    number_of_resolution = fields.Char(string='Número de resolución', compute='_compute_numero_control', store=True)
    @api.depends('sv_fe_receipt_stamp')
    def _compute_number_of_series_document(self):
        for record in self:
            if record.sv_fe_receipt_stamp:
                record.number_of_series_document = record.sv_fe_receipt_stamp
            else:
                record.number_of_series_document = ''
    number_of_series_document = fields.Char(string='Número de serie de documento (FEL)', compute='_compute_number_of_series_document')
    date_of_issue_voucher_of_liquidation = fields.Char(string='Fecha de emisión comprobante de liquidación')
    number_of_issue_voucher_of_liquidation = fields.Char(string='Número de comprobante de liquidación')
    resolution_of_voucher_of_liquidation = fields.Char(string='Resolución de comprobante de liquidación')
    series_of_voucher_of_liquidation = fields.Char(string='Serie de comprobante de liquidación')

    number_of_annexed_1 = fields.Integer(string='Número de anexo 1', default=1)
    number_of_annexed_2 = fields.Integer(string='Número de anexo 2', default=2)
    number_of_annexed_7 = fields.Integer(string='Número de anexo 7', default=7)
    number_of_annexed_10 = fields.Integer(string='Número de anexo 10', default=10)
    number_of_annexed_12 = fields.Integer(string='Número de anexo 12', default=12)

    number_of_annexed_3 = fields.Integer(string='Número de anexo 3', default=3)
    number_of_annexed_4 = fields.Integer(string='Número de anexo 4', default=4)
    number_of_annexed_5 = fields.Integer(string='Número de anexo 5', default=5)
    number_of_annexed_6 = fields.Integer(string='Número de anexo 6', default=6)
    number_of_annexed_8 = fields.Integer(string='Número de anexo 8', default=8)
    number_of_annexed_9 = fields.Integer(string='Número de anexo 9', default=9)
    number_of_annexed_11 = fields.Integer(string='Número de anexo 11', default=11)

    @api.depends('sv_fe_numero_control')
    def _compute_numero_control(self):
        for record in self:
            if record.sv_fe_numero_control:
                record.number_of_resolution = record.sv_fe_numero_control.replace("-", "")
            else:
                record.number_of_resolution = ''


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    type_of_purchase = fields.Selection([('1', '[1]Compras internas exentas'),
                                         ('2', '[2]Internaciones exentas'),
                                         ('3', '[3]Importaciones exentas y/o no sujetas'),
                                         ('4', '[4]Compras internas gravadas'),
                                         ('5', '[5]Internaciones gravadas de bienes'),
                                         ('6', '[6]Importaciones gravadas de bienes'),
                                         ('7', '[7]Importaciones de servicios gravados')],
                                        string='Tipo de compra')