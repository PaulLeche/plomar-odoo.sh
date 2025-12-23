# -*- coding: utf-8 -*-
import time
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class WizardPlanillaF930(models.TransientModel):
    _name = 'wizard.planilla.f930'
    _description = "Wizard reporte planilla f930"

    company_id = fields.Many2one('res.company', 'Empresa', required=True, default=lambda self: self.env.company)
    report_type = fields.Selection([('spreadsheet', 'Planilla')],
                                   string="Tipo de Reporte", required=True, readonly=True)
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


    def print_report_planilla_f910_xls(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': self.id,
            'model': 'wizard.planilla.f930',
            'form': data,
        }
        return self.env.ref('advanced_reports.action_report_planilla_f930_xls').report_action(self, data=datas)
