# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

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
                                                ('4', '[4]Costos artículos producidos/comprados importaciones/internaciones'),
                                                ('5', '[5]Costos artículos producidos/comprados interno'),
                                                ('6', '[6]Costos indirectos de fabricación'),
                                                ('7', '[7]Mano de obra')],
                                                string='Tipo de costo o gasto')

    type_of_operation = fields.Selection([('1', '[1]Gravada'),
                                          ('2', '[2]No Gravada'),
                                          ('3', '[3]Excluido o no constituye renta')],
                                          string='Tipo de operacion')

    def _prepare_invoice(self):
        res = super(PurchaseOrder, self)._prepare_invoice()
        res['document_classification'] = self.document_classification
        res['sector'] = self.sector
        res['type_of_cost_or_expense'] = self.type_of_cost_or_expense
        res['type_of_operation'] = self.type_of_operation
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    type_of_purchase = fields.Selection([('1', '[1]Compras internas exentas'),
                                         ('2', '[2]Internaciones exentas'),
                                         ('3', '[3]Importaciones exentas y/o no sujetas'),
                                         ('4', '[4]Compras internas gravadas'),
                                         ('5', '[5]Internaciones gravadas de bienes'),
                                         ('6', '[6]Importaciones gravadas de bienes'),
                                         ('7', '[7]Importaciones de servicios gravados')],
                                         string='Tipo de compra')

    def _prepare_account_move_line(self, move=False):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        res['type_of_purchase'] = self.type_of_purchase
        return res
