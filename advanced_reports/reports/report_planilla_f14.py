# -*- encoding: utf-8 -*-

from odoo.tools.translate import _
from odoo import fields, models, api
import json
from dateutil.relativedelta import relativedelta
from odoo.tools import float_round
import time, datetime

class ReportPlanillaF14(models.AbstractModel):
    _name = 'report.advanced_reports.report_planilla_f14'
    _description = 'report advanced_reports report_planilla_f14'


    def generate_records(self, record_ids):
        result = []
        totales = []
        date_from = record_ids.date_from
        date_to = record_ids.date_to
        company_id = record_ids.company_id
        payslip_ids = self.env['hr.payslip'].search([('state', 'in', ['paid']),
                                                 ('date_from', '>=', date_from),
                                                 ('date_to', '<=', date_to),
                                                 ('company_id', '=', company_id.id)], order='date,name')
        if payslip_ids:
            for payslip_id in payslip_ids:
                if payslip_id.employee_id.employee_partner:
                    employee_partner = payslip_id.employee_id.employee_partner
                else:
                    employee_partner = False
                domiciled = self.get_domiciled(employee_partner)
                country_code = self.get_country_code(employee_partner)
                nit = self.get_nit(employee_partner)
                dui = self.get_dui(employee_partner)
                if payslip_id.entry_code_id:
                    entry_code = payslip_id.entry_code_id.name
                else:
                    entry_code = ''
                basic_salary = self.get_amount(payslip_id, 'Salario básico')
                afp_amount = self.get_amount(payslip_id, 'AFP laboral')
                isss_amount = self.get_amount(payslip_id, 'ISSS laboral')
                if entry_code == '01' or entry_code == '60' or entry_code == '80':
                    basic_salary += afp_amount + isss_amount
                bonification_amount = self.get_amount(payslip_id,'Monto bonificaciones y gratificaciones')
                tax_amount = self.get_amount(payslip_id,'Impuesto retenido')
                exempt_bonus_amount = self.get_amount(payslip_id,'Aguinaldo exento')
                engraved_bonus_amount = self.get_amount(payslip_id, 'Aguinaldo grabado')
                inpep_amount = self.get_amount(payslip_id, 'INPEP')
                ipsfa_amount = self.get_amount(payslip_id, 'IPSFA')
                cefafa_amount = self.get_amount(payslip_id, 'CEFAFA')
                teacher_welfare_amount = self.get_amount(payslip_id, 'Bienestar Magisterial')
                isss_ivm_amount = self.get_amount(payslip_id, 'ISSS IVM')
                type_of_operation = self.get_type_of_operation(payslip_id.type_of_operation)
                classification = self.get_document_classification(payslip_id.document_classification)
                sector = self.get_sector(payslip_id.sector)
                type_cost = self.get_type_of_cost_or_expense(payslip_id.type_of_cost_or_expense)
                line = {
                    'domiciled': domiciled,
                    'country_code': country_code,
                    'name_partner': employee_partner.name.upper() if employee_partner else 'Sin contacto relacionado',
                    'nit': nit,
                    'dui': dui,
                    'entry_code': entry_code,
                    'basic_salary': basic_salary,
                    'bonification_amount': bonification_amount,
                    'tax_amount': tax_amount,
                    'exempt_bonus_amount': exempt_bonus_amount,
                    'engraved_bonus_amount': engraved_bonus_amount,
                    'afp_amount': afp_amount,
                    'isss_amount': isss_amount,
                    'inpep_amount': inpep_amount,
                    'ipsfa_amount': ipsfa_amount,
                    'cefafa_amount': cefafa_amount,
                    'teacher_welfare_amount': teacher_welfare_amount,
                    'isss_ivm_amount': isss_ivm_amount,
                    'type_of_operation': type_of_operation,
                    'classification': classification,
                    'sector': sector,
                    'type_cost': type_cost,
                    'period': payslip_id.period_mmaaaa if payslip_id.period_mmaaaa else '',
                    'paid_date': payslip_id.paid_date,
                }
                result.append(line)
            result = sorted(result, key=lambda d: (d['name_partner'], d['paid_date']))
            result = self.group_dictionary(result)
            result = sorted(result, key=lambda d: (d['name_partner']))
        return result, totales

    def group_dictionary(self, dictionary):
        partner_name1 = None
        group = []
        domiciled = ''
        country_code = ''
        nit = ''
        dui = ''
        entry_code = ''
        type_of_operation = ''
        classification = ''
        sector = ''
        type_cost = ''
        period = ''
        basic_salary = 0.0
        bonification_amount = 0.0
        tax_amount = 0.0
        exempt_bonus_amount = 0.0
        engraved_bonus_amount = 0.0
        afp_amount = 0.0
        isss_amount = 0.0
        inpep_amount = 0.0
        ipsfa_amount = 0.0
        cefafa_amount = 0.0
        teacher_welfare_amount = 0.0
        isss_ivm_amount = 0.0
        for line in dictionary:
            partner_name2 = line.get('name_partner')
            if (partner_name2 != partner_name1) and partner_name1:
                line_group = {
                    'domiciled': domiciled,
                    'country_code': country_code,
                    'name_partner': partner_name1,
                    'nit': nit,
                    'dui': dui,
                    'entry_code': entry_code,
                    'basic_salary': basic_salary,
                    'bonification_amount': bonification_amount,
                    'tax_amount': tax_amount,
                    'exempt_bonus_amount': exempt_bonus_amount,
                    'engraved_bonus_amount': engraved_bonus_amount,
                    'afp_amount': afp_amount,
                    'isss_amount': isss_amount,
                    'inpep_amount': inpep_amount,
                    'ipsfa_amount': ipsfa_amount,
                    'cefafa_amount': cefafa_amount,
                    'teacher_welfare_amount': teacher_welfare_amount,
                    'isss_ivm_amount': isss_ivm_amount,
                    'type_of_operation': type_of_operation,
                    'classification': classification,
                    'sector': sector,
                    'type_cost': type_cost,
                    'period': period,
                }
                group.append(line_group)
                basic_salary = 0.0
                bonification_amount = 0.0
                tax_amount = 0.0
                exempt_bonus_amount = 0.0
                engraved_bonus_amount = 0.0
                afp_amount = 0.0
                isss_amount = 0.0
                inpep_amount = 0.0
                ipsfa_amount = 0.0
                cefafa_amount = 0.0
                teacher_welfare_amount = 0.0
                isss_ivm_amount = 0.0

            domiciled = line.get('domiciled')
            country_code = line.get('country_code')
            partner_name1 = line.get('name_partner')
            nit = line.get('nit')
            dui = line.get('dui')
            entry_code = line.get('entry_code')
            basic_salary += line.get('basic_salary')
            bonification_amount += line.get('bonification_amount')
            tax_amount += line.get('tax_amount')
            exempt_bonus_amount += line.get('exempt_bonus_amount')
            engraved_bonus_amount += line.get('engraved_bonus_amount')
            afp_amount += line.get('afp_amount')
            isss_amount += line.get('isss_amount')
            inpep_amount += line.get('inpep_amount')
            ipsfa_amount += line.get('ipsfa_amount')
            cefafa_amount += line.get('cefafa_amount')
            teacher_welfare_amount += line.get('teacher_welfare_amount')
            isss_ivm_amount += line.get('isss_ivm_amount')
            type_of_operation = line.get('type_of_operation')
            classification = line.get('classification')
            sector = line.get('sector')
            type_cost = line.get('type_cost')
            period = line.get('period')


        if partner_name1:
            line_group = {
                'domiciled': domiciled,
                'country_code': country_code,
                'name_partner': partner_name1,
                'nit': nit,
                'dui': dui,
                'entry_code': entry_code,
                'basic_salary': basic_salary,
                'bonification_amount': bonification_amount,
                'tax_amount': tax_amount,
                'exempt_bonus_amount': exempt_bonus_amount,
                'engraved_bonus_amount': engraved_bonus_amount,
                'afp_amount': afp_amount,
                'isss_amount': isss_amount,
                'inpep_amount': inpep_amount,
                'ipsfa_amount': ipsfa_amount,
                'cefafa_amount': cefafa_amount,
                'teacher_welfare_amount': teacher_welfare_amount,
                'isss_ivm_amount': isss_ivm_amount,
                'type_of_operation': type_of_operation,
                'classification': classification,
                'sector': sector,
                'type_cost': type_cost,
                'period': period,
            }
            group.append(line_group)
        return group


    def get_nit(self, partner):
        if partner:
            if partner.sv_fe_identification_type == '36' and partner.vat:
                return partner.vat
            else:
                return ''
        else:
            return ''
    def get_dui(self, partner):
        if partner:
            # if partner.sv_fe_identification_type == '13' and partner.dui_field:
            if partner.dui_field:
                return partner.dui_field
            else:
                return ''
        else:
            return ''
    def get_domiciled(self, partner):
        if partner:
            if partner.domiciled_id:
                return partner.domiciled_id.name
            else:
                return ''
        else:
            return ''
    def get_country_code(self, partner):
        country_code = ''
        if partner:
            if partner.country_id:
                if partner.country_id.country_code:
                    country_code = partner.country_id.country_code
        return country_code

    def get_amount(self,payslip, rule_name):
        amount = 0.0
        if payslip.line_ids:
            amount += sum(line.amount for line in payslip.line_ids.filtered(lambda l: l.name == rule_name))
        return amount

    def get_type_of_operation(self, type_of_operation):
        if type_of_operation:
            if type_of_operation == '1':
                return '[1]Grabada'
            elif type_of_operation == '2':
                return '[2]No Grabada'
            elif type_of_operation == '3':
                return '[3]Excuido o no constituye renta'
            elif type_of_operation == '4':
                return '[4]Mixta'
            else:
                return ''
        else:
            return ''

    def get_document_classification(self, document_classification):
        if document_classification:
            if document_classification == '1':
                return '[1]Costo'
            elif document_classification == '2':
                return '[2]Gasto'
            else:
                return ''
        else:
            return ''

    def get_sector(self, sector):
        if sector:
            if sector == '1':
                return '[1]Industria'
            elif sector == '2':
                return '[2]Comercio'
            elif sector == '3':
                return '[3]Agropecuaria'
            elif sector == '4':
                return '[4]servicios, Profesiones, Arte y Oficios'
            else:
                return ''
        else:
            return ''


    def get_type_of_cost_or_expense(self, type_of_cost_or_expense):
        if type_of_cost_or_expense:
            if type_of_cost_or_expense == '1':
                return '[1]Gasto de venta sin donacion'
            elif type_of_cost_or_expense == '2':
                return '[2]Gasto de administracion sin donacion'
            elif type_of_cost_or_expense == '3':
                return '[3]Gasto financiero sin donacion'
            elif type_of_cost_or_expense == '4':
                return '[4]Costos artículos producidos/comprados importaciones/internaciones'
            elif type_of_cost_or_expense == '5':
                return '[5]Costos artículos producidos/comprados interno'
            elif type_of_cost_or_expense == '6':
                return '[6]Costos indirectos de fabricación'
            elif type_of_cost_or_expense == '7':
                return '[7]Mano de obra'
            else:
                return ''
        else:
            return ''




