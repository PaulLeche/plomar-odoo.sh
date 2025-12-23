# -*- encoding: utf-8 -*-

from odoo.tools.translate import _
from odoo import fields, models, api
import json
from dateutil.relativedelta import relativedelta
from odoo.tools import float_round
import time, datetime
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)

class ReportCloseBox(models.AbstractModel):
    _name = 'report.advanced_reports.report_close_box_commission'
    _description = 'report advanced_reports report_close_box_commission'

    def _get_format_date(self, date):
        B = str(self._month_letters(date.month))
        return date.strftime('%d de ' + B + ' del %Y')

    def get_product_names(self, invoice_lines):
        return ', '.join(invoice_lines.mapped('product_id.name')) if invoice_lines else ''

    def get_invoice_payment_line(self, payment, invoice):
        invoice_amount = invoice.amount_total if invoice else 0.00
        payment_amount = min(payment.amount, invoice_amount) if invoice else payment.amount
        sale_order_id = False
        payment_days = 0
        is_exento_export = False
        if invoice:
            if invoice.invoice_line_ids and invoice.invoice_line_ids[0].sale_line_ids:
                if invoice.invoice_line_ids[0].sale_line_ids[0].order_id:
                    sale_order_id = invoice.invoice_line_ids[0].sale_line_ids[0].order_id
            if payment:
                payment_days = (payment.date - invoice.invoice_date).days
            is_exento_export = self.is_exento_export(invoice.invoice_line_ids)
        return {
            'invoice_invoice_date': invoice.invoice_date if invoice else '',
            'invoice_date': payment.date or '',
            'partner_name': payment.partner_id.name or '',
            'numero_control': invoice.numero_control or '' if invoice else '',
            'chashier': payment.cashier_id.name if payment.cashier_id else '',
            'invoice_lines': self.get_product_names(invoice.invoice_line_ids) if invoice else '', 
            'amount_untaxed': invoice.amount_untaxed if invoice else '',
            'amount_tax': invoice.amount_tax if invoice else '',
            'invoice_total': invoice_amount,
            'amount_total': payment_amount if is_exento_export != False else payment_amount/1.13,
            'payment_term': invoice.invoice_payment_term_id.display_name if invoice else '',
            'payment_method': payment.box_payment_method_id.name if payment.box_payment_method_id else '',
            'saler_name': invoice.invoice_user_id.name if invoice else '',
            'payment_days': payment_days,
            'name_sale': sale_order_id.name if sale_order_id else "-"
        }
            
    def _month_letters(self, mes):
        switcher = {
            1: "Enero",
            2: "Febrero",
            3: "Marzo",
            4: "Abril",
            5: "Mayo",
            6: "Junio",
            7: "Julio",
            8: "Agosto",
            9: "Septiembre",
            10: "Octubre",
            11: "Noviembre",
            12: "Diciembre"
        }
        return switcher.get(mes, "Invalid month")
    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        totales = self.generate_records(docs)
        date_from = self._get_format_date(docs.date_from)
        date_to = self._get_format_date(docs.date_to)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'self': self,
            'ultima': totales,
            'date_from': date_from,
            'date_to': date_to,
        }
        return docargs

    def generate_records(self, record_ids):
        # total = defaultdict(list)
        total = []
        date_from = record_ids.date_from
        date_to = record_ids.date_to
        company_id = record_ids.company_id
        box_number_ids = record_ids.box_number_ids
        payments = self.env['account.payment'].search([('payment_type', 'in', ['inbound']),
                                                 ('state', '=', 'posted'),
                                                 ('date', '>=', date_from),
                                                 ('date', '<=', date_to),
                                                 ('company_id', '=', company_id.id)], order='date,name')
        if payments:
            for box in box_number_ids:
                result = []
                box_name = box.name
                for payment in payments.filtered(lambda l: l.box_number_id.id == box.id):
                    if payment.reconciled_invoice_ids:
                        for invoice in payment.reconciled_invoice_ids:
                            result.append(self.get_invoice_payment_line(payment,invoice))
                    else:
                        result.append(self.get_invoice_payment_line(payment,None))
                        
                result.sort(key=lambda x: x['payment_method'])
                # total[box_name].extend(result)
                total.append([box_name, result])

            # total = self.separate_by_cashier(total)
        return total

    def separate_by_cashier(self, total):
        separated = []

        for caja in total:
            caja_name = caja[0]
            transactions = caja[1]

            cashier_dict = defaultdict(list)

            for transaction in transactions:
                cashier_dict[transaction['chashier']].append(transaction)

            for cashier, trans_list in cashier_dict.items():
                separated.append([caja_name, cashier, trans_list])

        return separated


    def is_exento_export(self, lines):
        if len(lines) == self.vat_verification(lines, 'exento'):
            return True
        else:
            if len(lines) == self.vat_verification(lines, 'exportaciones'):
                return True
            else:
                cont = 0
                for line in lines:
                    if not line.tax_ids:
                        cont += 1
                if len(lines) == cont:
                    return True
        return False

    def vat_verification(self, lines, string):
        cont = 0
        for line in lines:
            if all(string in tax.name.lower() for tax in line.tax_ids):
                cont += 1
        return cont

