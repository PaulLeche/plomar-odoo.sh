# -*- encoding: utf-8 -*-

from odoo.tools.translate import _
from odoo import fields, models, api
import json
from dateutil.relativedelta import relativedelta
from odoo.tools import float_round
import time, datetime
from collections import defaultdict

class ReportCloseBox(models.AbstractModel):
    _name = 'report.advanced_reports.report_close_box'
    _description = 'report advanced_reports report_close_box'

    def _get_format_date(self, date):
        B = str(self._month_letters(date.month))
        return date.strftime('%d de ' + B + ' del %Y')

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
            'company_name': docs.company_id.name if docs.company_id else ''
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
                        if payment.reconciled_invoice_ids[0].numero_control:
                            numero_control = payment.reconciled_invoice_ids[0].numero_control
                        else:
                            numero_control = ''
                    else:
                        numero_control = ''

                    line = {
                        'chashier': payment.cashier_id.name if payment.cashier_id else '',
                        'partner_name': payment.partner_id.name if payment.partner_id.name else '',
                        'invoice_date': payment.date if payment.date else False,
                        'numero_control': numero_control,
                        'amount_total': payment.amount if payment.amount else 0.0,
                        'payment_method': payment.box_payment_method_id.name if payment.box_payment_method_id else '',
                    }
                    result.append(line)
                result.sort(key=lambda x: x['payment_method'])
                # total[box_name].extend(result)
                total.append([box_name, result])

            total = self.separate_by_cashier(total)
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