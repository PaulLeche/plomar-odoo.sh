# -*- coding: utf-8 -*-
import time
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class WizardCloseBox(models.TransientModel):
    _name = 'wizard.close.box.commission'
    _description = "Wizard de cierre de caja para comisión"

    company_id = fields.Many2one('res.company', 'Empresa', required=True, default=lambda self: self.env.company)
    report_type = fields.Selection([('box', 'Caja')],
                                   string="Tipo de Reporte", required=True, readonly=True)

    def _get_first_day_of_month(self):
        first_day_of_month = date.today()
        return first_day_of_month
    def _get_last_day_of_month(self):
        last_day_of_month = date.today()
        return last_day_of_month

    date_from = fields.Date('Fecha desde', required=True, default=lambda self: self._get_first_day_of_month())
    date_to = fields.Date('Fecha hasta', required=True, default=lambda self: self._get_last_day_of_month())
    # box1 = fields.Boolean(string="Caja 1")
    # box2 = fields.Boolean(string="Caja 2")
    box_number_ids = fields.Many2many('box.number', string="Cajas", required=True)
    

    def print_report_close_box_commission_xls(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': self.id,
            'model': 'wizard.close.box',
            'form': data,
        }
        return self.env.ref('advanced_reports.action_close_box_commission_xls').report_action(self, data=datas)