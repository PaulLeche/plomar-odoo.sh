# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil import relativedelta
from odoo import models, fields, api


class BoxPaymentMethod(models.Model):
    _name = 'box.payment.method'
    _description = "Método de pago caja"

    name = fields.Char(string="Metodo de pago")
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company)