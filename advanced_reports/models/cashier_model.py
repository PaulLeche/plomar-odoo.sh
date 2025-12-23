# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil import relativedelta
from odoo import models, fields, api


class CashierModel(models.Model):
    _name = 'cashier.model'
    _description = "Cajero"

    name = fields.Char(string="Nombre del cajero")
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company)
