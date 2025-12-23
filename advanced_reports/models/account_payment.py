# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class AccountPayment(models.Model):
    _inherit = "account.payment"

    cashier_id = fields.Many2one('cashier.model', string="Nombre del cajero")
    box_number_id = fields.Many2one('box.number', string="Número de caja")
    box_payment_method_id = fields.Many2one('box.payment.method', string="Método de pago")








