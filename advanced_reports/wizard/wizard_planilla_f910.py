# -*- coding: utf-8 -*-
import time
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class WizardPlanillaF910(models.TransientModel):
    _name = 'wizard.planilla.f910'
    _description = "Wizard reporte planilla f910"

    company_id = fields.Many2one('res.company', 'Empresa', required=True, default=lambda self: self.env.company)
    report_type = fields.Selection([('spreadsheet', 'Planilla')],
                                   string="Tipo de Reporte", required=True, readonly=True)

    def _get_years(self):
        return [(str(year), str(year)) for year in range(2000, datetime.now().year + 1)]


    year = fields.Selection(selection='_get_years', string="Año a declarar", required=True, default=str(datetime.now().year))

    exempt_bonus = fields.Float(string="Aguinaldo exento (determinado por el Ministerio de Hacienda)",
                                    digits=(16, 2))
    company_currency_id = fields.Many2one('res.currency',
                                          string="Moneda de la empresa",
                                          related='company_id.currency_id',
                                          readonly=True,
                                          store=True)


    def print_report_planilla_f910_xls(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': self.id,
            'model': 'wizard.planilla.f910',
            'form': data,
        }
        return self.env.ref('advanced_reports.action_report_planilla_f910_xls').report_action(self, data=datas)
