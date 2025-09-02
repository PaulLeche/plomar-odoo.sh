# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil import relativedelta
from odoo import models, fields, api


class BoxNumber(models.Model):
    _name = 'box.number'
    _description = "Número de caja"

    name = fields.Char(string="Número de caja")
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company)

