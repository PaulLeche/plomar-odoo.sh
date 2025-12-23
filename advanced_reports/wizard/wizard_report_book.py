# -*- coding: utf-8 -*-
import time
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class WizardBalanceAging(models.TransientModel):
    _name = 'wizard.report.book'
    _description = "Wizard de reportes de venta y compra"

    company_id = fields.Many2one('res.company', 'Empresa', required=True,default=lambda self: self.env.company)
    report_type = fields.Selection([('sale_taxpayer', 'Venta contribuyente'),
                                    ('sale_consumer', 'Venta consumidor final'),
                                    ('purchase', 'Compras')],
                                   string="Tipo de Reporte" ,required=True, readonly=True)

    def _get_first_day_of_month(self):
        today = date.today()
        first_day_of_month = today.replace(day=1)
        return first_day_of_month

    def _get_last_day_of_month(self):
        today = date.today()
        last_day_of_month = today.replace(day=1) + relativedelta(months=1, days=-1)
        return last_day_of_month

    date_from = fields.Date('Fecha desde', required=True, default=lambda self: self._get_first_day_of_month())
    date_to = fields.Date('Fecha hasta', required=True, default=lambda self: self._get_last_day_of_month())
    # journal_ids = fields.Many2many('account.journal', string="Diarios", required=False)

    def print_report_sale_taxpayer_xls(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': self.id,
            'model': 'wizard.report.book',
            'form': data,
        }
        return self.env.ref('advanced_reports.action_sale_taxpayer_xls').report_action(self, data=datas)

    def print_report_sale_taxpayer_pdf(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': self.id,
            'model': 'wizard.report.book',
            'form': data,
        }
        return self.env.ref('advanced_reports.action_sale_taxpayer_pdf').report_action(self, data=datas)

    def print_report_sale_consumer_pdf(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': self.id,
            'model': 'wizard.report.book',
            'form': data,
        }
        return self.env.ref('advanced_reports.action_sale_consumer_pdf').report_action(self, data=datas)

    def print_report_sale_consumer_xls(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': self.id,
            'model': 'wizard.report.book',
            'form': data,
        }
        return self.env.ref('advanced_reports.action_sale_consumer_xls').report_action(self, data=datas)

    def print_report_purchase_pdf(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': self.id,
            'model': 'wizard.report.book',
            'form': data,
        }
        return self.env.ref('advanced_reports.action_purchase_pdf').report_action(self, data=datas)

    def print_report_purchase_xls(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': self.id,
            'model': 'wizard.report.book',
            'form': data,
        }
        return self.env.ref('advanced_reports.action_purchase_xls').report_action(self, data=datas)

