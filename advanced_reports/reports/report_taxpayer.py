# -*- encoding: utf-8 -*-

from odoo.tools.translate import _
from odoo import fields, models, api
from odoo.tools.misc import formatLang
from datetime import datetime, time
import json
from dateutil.relativedelta import relativedelta
from odoo.tools import float_round


class ReportTaxpayer(models.AbstractModel):
    _name = 'report.advanced_reports.report_taxpayer'
    _description = 'report advanced_reports report_taxpayer'

    def _get_format_date(self, date):
        B = str(self._month_letters(date.month))
        return date.strftime('%d de ' + B + ' del %Y')

    def _format_price(self, price, currency_id):
        if not price:
            return '0.00'
        amount_f = formatLang(self.env, price, dp='Product Price',
                              currency_obj=currency_id)
        amount_f = amount_f.replace(currency_id.symbol, '').strip()
        result = amount_f.replace(',', '')
        format_final = '{0:,.2f}'.format(float(result))
        return format_final

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
        result, totales = self.generate_records(data)
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        if docs:
            date_from = self._get_format_date(docs.date_from)
            date_to = self._get_format_date(docs.date_to)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'self': self,
            'data': result,
            'ultima': totales,
            'date_from': date_from,
            'date_to': date_to,
            'format_price': self._format_price,
        }
        return docargs

    def generate_records(self, record_ids):
        result = []
        totales = []
        f_propias_exenta = 0.0
        f_propias_no_sujetas = 0.0
        f_propias_grabada = 0.0
        f_propias_debito = 0.0
        f_terceros_exenta = 0.0
        f_terceros_grabada = 0.0
        f_terceros_debito = 0.0
        f_iva_ret =0.0
        f_propina = 0.0
        f_imp_turismo = 0.0
        f_total_ventas = 0.0
        date_from = datetime.strptime(record_ids['form']['date_from'], '%Y-%m-%d').date()
        date_to = datetime.strptime(record_ids['form']['date_to'], '%Y-%m-%d').date()
        start_datetime = datetime.combine(date_from, time.min)  # 00:00:00
        end_datetime = datetime.combine(date_to, time.max).replace(microsecond=0)  # 23:59:59
        date_from_str = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
        date_to_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        company = record_ids['form']['company_id'][0]
        company_id = self.env['res.company'].browse(company)
        invoices = self.env['account.move'].search([
            ('state', 'in', ['posted']),
            ('date_certification', '>=', date_from_str),
            ('date_certification', '<=', date_to_str),
            ('move_type', 'in', ['out_invoice']),
            ('company_id', '=', company_id.id)], order='date,name')
        if invoices:
            for invoice in invoices.filtered(lambda l:l.fe_type == '03'):
                propias_exenta = 0.0
                propias_no_sujetas = 0.0
                propias_grabada = 0.0
                propias_debito = 0.0
                terceros_exenta = 0.0
                terceros_grabada = 0.0
                terceros_debito = 0.0
                iva_ret = 0.0
                total_ventas = 0.0
                propina = 0.0
                imp_turismo = 0.0
                for l in invoice.invoice_line_ids:
                    pre_grab = 0.0
                    pre_deb = 0.0
                    if company_id.currency_id != l.currency_id:
                        precio = l.currency_id._convert(l.price_total, company_id.currency_id, company_id, invoice.invoice_date)
                    else:
                        precio = l.price_total

                    taxes = l.tax_ids.compute_all(l.price_unit, company_id.currency_id, l.quantity, l.product_id,invoice.partner_id)
                    propias_grabada_ini = 0.0
                    for tax in taxes['taxes']:
                        imp = self.env['account.tax'].browse(tax['id'])
                        if 'exento' in imp.name.lower():
                            propias_exenta += precio
                        if 'iva por pagar contribuyentes' in imp.name.lower():
                            pre_grab = tax['base']
                            pre_deb = tax['amount']
                            if company_id.currency_id != l.currency_id:
                                pre_grab = l.currency_id._convert(pre_grab, company_id.currency_id, company_id,invoice.invoice_date)
                                pre_deb = l.currency_id._convert(pre_deb, company_id.currency_id, company_id,invoice.invoice_date)
                                if propias_grabada_ini == 0.0:
                                    propias_grabada_ini += pre_grab
                                propias_grabada_ini += pre_deb
                            else:
                                if propias_grabada_ini == 0.0:
                                    propias_grabada_ini += pre_grab
                                propias_grabada_ini += pre_deb

                        if 'gran contribuyente' in imp.name.lower():
                            subprecio = tax['amount']
                            if company_id.currency_id != l.currency_id:
                                subprecio = l.currency_id._convert(subprecio, company_id.currency_id, company_id,invoice.invoice_date)
                                iva_ret += subprecio
                            else:
                                iva_ret += subprecio
                        if 'turismo' in imp.name.lower():
                            subprecio = tax['amount']
                            if company_id.currency_id != l.currency_id:
                                subprecio = l.currency_id._convert(subprecio, company_id.currency_id, company_id,invoice.invoice_date)
                                imp_turismo += subprecio
                            else:
                                imp_turismo += subprecio

                    propias_grabada += propias_grabada_ini
                    if not l.tax_ids:
                        if l.product_id and ('propinas' in l.product_id.name.lower()):
                            propina += precio
                        else:
                            propias_no_sujetas += precio

                if company_id.currency_id != l.currency_id:
                    total = invoice.currency_id._convert(invoice.amount_total, company_id.currency_id, company_id,invoice.invoice_date)
                    total_ventas += total
                else:
                    total_ventas += invoice.amount_total
                # total_ventas = propias_exenta+propias_no_sujetas+propias_grabada+propias_debito+terceros_exenta+terceros_grabada+terceros_debito+abs(iva_ret)+propina+imp_turismo
                linea = {
                    'fecha_emision': self.char_to_date(invoice.date_certification) if invoice.date_certification else False,
                    'nro_doc': invoice.numero_control if invoice.numero_control else '',
                    'nrc': self.insert_dash_before_last_nrc(invoice.partner_id.nrc) if invoice.partner_id.nrc else '',
                    'nombre_cliente': invoice.partner_id.name or '',
                    'propias_exenta': propias_exenta,
                    'propias_no_sujetas': propias_no_sujetas,
                    'propias_grabada': propias_grabada,
                    'propias_debito': propias_debito,
                    'terceros_exenta': terceros_exenta,
                    'terceros_grabada': terceros_grabada,
                    'terceros_debito': terceros_debito,
                    'iva_ret': abs(iva_ret),
                    'propina': propina,
                    'imp_turismo': imp_turismo,
                    'total': total_ventas,
                }
                result.append(linea)
                f_propias_exenta += propias_exenta
                f_propias_no_sujetas += propias_no_sujetas
                f_propias_grabada += propias_grabada
                f_propias_debito += propias_debito
                f_terceros_exenta += terceros_exenta
                f_terceros_grabada += terceros_grabada
                f_terceros_debito += terceros_debito
                f_iva_ret += abs(iva_ret)
                f_propina += propina
                f_imp_turismo += imp_turismo
                f_total_ventas += total_ventas
            totales = {
                'f_propias_exenta': f_propias_exenta,
                'f_propias_no_sujetas': f_propias_no_sujetas,
                'f_propias_grabada': f_propias_grabada,
                'f_propias_debito': f_propias_debito,
                'f_terceros_exenta': f_terceros_exenta,
                'f_terceros_grabada': f_terceros_grabada,
                'f_terceros_debito': f_terceros_debito,
                'f_iva_ret': f_iva_ret,
                'f_propina': f_propina,
                'f_imp_turismo': f_imp_turismo,
                'f_total_ventas': f_total_ventas,
                'company_name': company_id.name if company_id and company_id.name else '',
                'giro': self.get_giro(company_id.partner_id) if company_id.partner_id else '',
            }
        return result, totales

    def insert_dash_before_last_nrc(self, nrc):
        if len(nrc) > 1:
            return nrc[:-1] + '-' + nrc[-1]
        return nrc

    def get_giro(self, partner_id):
        giro = ''
        if partner_id.fe_code_activity:
            if partner_id.fe_code_activity.activity_name:
                giro = partner_id.fe_code_activity.activity_name
        return giro

    def char_to_date(self, fecha_str):
        return datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S").date()
