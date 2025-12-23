# -*- encoding: utf-8 -*-

from odoo.tools.translate import _
from odoo import fields, models, api
import json
from dateutil.relativedelta import relativedelta
from odoo.tools import float_round
from datetime import date, timedelta

class ReportPlanillaF910(models.AbstractModel):
    _name = 'report.advanced_reports.report_planilla_f910'
    _description = 'report advanced_reports report_planilla_f910'


    def get_amount(self,payslip, rule_name):
        amount = 0.0
        if payslip.line_ids:
            amount += sum(line.amount for line in payslip.line_ids.filtered(lambda l: l.name == rule_name))
        return amount

    def get_amount_bon_gratificaciones(self, payslip):
        ingreso = 0.0
        aguinaldo = 0.0
        if payslip.line_ids:
            for line in payslip.line_ids:
                if line.category_id.code == 'ING':
                    ingreso += line.total
                if line.code == 'AGUI':
                    aguinaldo += line.total
        return ingreso - aguinaldo


    def get_amount_input(self, payslip, type):
        amount = 0.0
        if payslip.input_line_ids:
            amount += sum(line.amount for line in payslip.input_line_ids.filtered(lambda l: l.input_type_id.name == type))
        return amount

    def get_nit(self, partner):
        if partner:
            if partner.sv_fe_identification_type == '36' and partner.vat:
                return partner.vat
            else:
                return ''
        else:
            return ''
    def generate_records(self, record_ids):
        result = []
        totales = []
        date_from = date(int(record_ids.year), 1, 1)
        date_to = date(int(record_ids.year), 12, 31)
        company_id = record_ids.company_id

        latest_payslip = ''

        payslip_ids = self.env['hr.payslip'].search([('state', 'in', ['paid']),
                                                     ('date_from', '>=', date_from),
                                                     ('date_to', '<=', date_to),
                                                     ('company_id', '=', company_id.id)], order='date,name')

        if payslip_ids:
            employee_ids_list = []
            for payslip in payslip_ids:
                if payslip.employee_id.id not in employee_ids_list:
                    employee_ids_list.append(payslip.employee_id.id)
            for employee in employee_ids_list:
                line = {}
                employee_id = self.env['hr.employee'].browse(employee)
                line['employee_id'] = employee_id.name
                line['nit'] = self.get_nit(employee_id.employee_partner)

                line['cod_ingreso'] = ''

                monto_deve = 0.0
                bonificacion_grat = 0.0
                imp_retenido = 0.0
                aguinaldo_ex = 0.0
                aguinaldo_grab = 0.0
                isss = 0.0
                afp = 0.0
                ipsfa = 0.0
                cefafa = 0.0
                inep = 0.0
                bien_magisterial = 0.0

                cod_ingreso = ''

                for month in range(1, 13):
                    # Definir la fecha de inicio y fin del mes
                    date_from = date(int(record_ids.year), month, 1)
                    if month == 12:
                        date_to = date(int(record_ids.year), month, 31)
                    else:
                        date_to = date(int(record_ids.year), month + 1, 1) - timedelta(days=1)

                    payslip_employee = self.env['hr.payslip'].search([('state', 'in', ['paid']),
                                                                      ('employee_id', '=', employee),
                                                                      ('date_from', '>=', date_from),
                                                                      ('date_to', '<=', date_to),
                                                                      ('company_id', '=', company_id.id)])
                    sujeto_ret = 0.0
                    imp_renta = 0.0
                    afp_lab = 0.0

                    if payslip_employee:
                        latest_payslip = sorted(payslip_employee, key=lambda p: p.date_to, reverse=True)[0]
                        cod_ingreso = latest_payslip.entry_code_id.name if latest_payslip.entry_code_id and latest_payslip.entry_code_id.name else ''

                    for hr in payslip_employee:
                        sujeto_ret += self.get_amount(hr , 'Monto Sujeto de Retencion')
                        imp_renta += self.get_amount(hr , 'Impuesto sobre la Renta')
                        afp_lab += self.get_amount(hr , 'AFP laboral')
                        isss += self.get_amount(hr , 'ISSS')
                        afp += self.get_amount(hr, 'AFP')
                        ipsfa += self.get_amount(hr, 'IPSFA')
                        cefafa += self.get_amount(hr, 'CEFAFA')
                        inep += self.get_amount(hr, 'INPEP')
                        bien_magisterial += self.get_amount(hr, 'Bienestar magisterial')
                        aguinaldo_grab += self.get_amount_input(hr, 'Aguinaldo')
                        bonificacion_grat += self.get_amount_bon_gratificaciones(hr)
                        monto_deve += self.get_amount(hr, 'Monto Sujeto de Retencion')

                    line[str(month) + 'ret'] = abs(sujeto_ret)
                    line[str(month) + 'renta'] = abs(imp_renta)
                    imp_retenido += abs(imp_renta)
                    line[str(month) + 'lab'] = abs(afp_lab)


                line['cod_ingreso'] = cod_ingreso

                line['monto_deve'] = monto_deve - abs(bonificacion_grat)
                line['bonificacion_grat'] = abs(bonificacion_grat)
                line['imp_retenido'] = imp_retenido
                line['aguinaldo_ex'] = record_ids.exempt_bonus if record_ids.exempt_bonus else aguinaldo_ex
                line['aguinaldo_grab'] = aguinaldo_grab
                line['isss'] = abs(isss)
                line['afp'] = abs(afp)
                line['ipsfa'] = abs(ipsfa)
                line['cefafa'] = abs(cefafa)
                line['inep'] = abs(inep)
                line['bien_magisterial'] = abs(bien_magisterial)
                line['year'] = record_ids.year
                result.append(line)


        return result, totales
