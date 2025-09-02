# -*- encoding: utf-8 -*-

from odoo.tools.translate import _
from odoo import fields, models, api
import json
from dateutil.relativedelta import relativedelta
from odoo.tools import float_round
from datetime import date, timedelta

class ReportPlanillaF930(models.AbstractModel):
    _name = 'report.advanced_reports.report_planilla_f930'
    _description = 'report advanced_reports report_planilla_f930'

    def get_nit(self, partner):
        if partner.identification_type == '36':
            if partner.vat:
                return partner.vat
            else:
                return ''
        else:
            return ''

    def get_code_document(self, move):
        code_document = ''
        if move.fe_type:
            if move.fe_type == '01':
                code_document = '6'
            elif move.fe_type == '03':
                code_document = '1'
            elif move.fe_type == '05':
                code_document = '5'
            elif move.fe_type == '06':
                code_document = '4'
            elif move.fe_type == '14':
                code_document = '7'
        return code_document

    def get_number_document(self, move):
        if move.move_type == 'in_invoice':
            if move.document_number:
                return move.document_number
            else:
                return ''
        else:
            if move.move_type == 'out_invoice':
                if move.numero_control:
                    return move.numero_control
                else:
                    return ''
            else:
                return ''



    def generate_records(self, record_ids):
        result = []
        totales = []
        date_from = record_ids.date_from
        date_to = record_ids.date_to
        company_id = record_ids.company_id
        moves = self.env['account.move'].search([('move_type', 'in', ['in_invoice', 'out_invoice']),
                                                 ('state', '=', 'posted'),
                                                 ('invoice_date', '>=', date_from),
                                                 ('invoice_date', '<=', date_to),
                                                 ('company_id', '=', company_id.id)], order='date,name')
        if moves:
            for move in moves:
                imp = False
                subject_amount = 0.0
                ret_amount = 0.0
                modality = ''
                for l in move.invoice_line_ids:
                    subject = 0.0
                    if l.tax_ids:
                        taxes = l.tax_ids.compute_all(l.price_unit, company_id.currency_id, l.quantity, l.product_id, move.partner_id)
                        for tax in taxes['taxes']:
                            imp = self.env['account.tax'].browse(tax['id'])
                            if 'percepción de iva' in imp.name.lower() and move.move_type == 'in_invoice':
                                imp = True
                                if subject == 0.0:
                                    subject += l.price_total
                                ret_amount += tax['amount']
                                modality = '1'
                            elif 'Anticipo a cuenta' in imp.name.lower() and move.move_type == 'in_invoice':
                                imp = True
                                if subject == 0.0:
                                    subject += l.price_total
                                ret_amount += tax['amount']
                                modality = '2'
                            elif 'gran contribuyente' in imp.name.lower() and move.move_type == 'out_invoice':
                                imp = True
                                if subject == 0.0:
                                    subject += l.price_total
                                ret_amount += tax['amount']
                                modality = '3'
                        subject_amount += subject
                if imp == True:
                    number_document = self.get_number_document(move)
                    line = {
                        'nit': self.get_nit(move.partner_id),
                        'partner_name': move.partner_id.name if move.partner_id.name else '',
                        'quality': '1',
                        'modality': modality,
                        'code_document': self.get_code_document(move),
                        'date_move': move.invoice_date,
                        'serie_document':  move.number_of_series_document if move.number_of_series_document else '',
                        'number_document': number_document,
                        'subject_amount': subject_amount,
                        'ret_amount': abs(ret_amount),
                        'period': move.period_mmaaaa,
                    }
                    result.append(line)

        return result, totales

