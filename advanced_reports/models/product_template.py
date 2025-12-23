# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil import relativedelta
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    reference_books = fields.Selection([
        ('costs', '01- Costos'),
        ('retaceos', '02- Retaceos'),
        ('local', '03- Compras Locales')
    ], string="Referencia en libros")

