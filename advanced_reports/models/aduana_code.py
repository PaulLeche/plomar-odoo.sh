# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil import relativedelta
from odoo import models, fields, api


class AduanaCode(models.Model):
    _name = 'aduana.code'
    _description = "Código de aduana"

    name = fields.Char(string="Código")
    name_cod = fields.Char(string="Aduana")