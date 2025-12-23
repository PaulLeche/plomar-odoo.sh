# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    cashier_id = fields.Many2one('cashier.model', string="Nombre del cajero")
    box_number_id = fields.Many2one('box.number', string="Número de caja")
    box_payment_method_id = fields.Many2one('box.payment.method', string="Método de pago")



    def _create_payment_vals_from_wizard(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        if self.cashier_id:
            res['cashier_id'] = self.cashier_id.id
        if self.box_number_id:
            res['box_number_id'] = self.box_number_id.id
        if self.box_payment_method_id:
            res['box_payment_method_id'] = self.box_payment_method_id.id
        return res