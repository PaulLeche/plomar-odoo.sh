# -*- encoding: utf-8 -*-

from odoo.tools.translate import _
from odoo import fields, models, api
import json
from dateutil.relativedelta import relativedelta
from odoo.tools import float_round
from datetime import datetime, time

class ReportConsumer(models.AbstractModel):
    _name = 'report.advanced_reports.report_consumer'
    _description = 'report advanced_reports report_consumer'

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
        }
        return docargs

    def generate_records(self, record_ids):
        result = []
        totales = []

        f_propias_exenta = 0.0
        f_venta_no_sujeta = 0.0
        f_venta_local = 0.0
        f_venta_exportacion = 0.0
        f_iva_13 = 0.0
        f_retencion_1 = 0.0
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
            for invoice in invoices.filtered(lambda l:l.fe_type == '01' or l.fe_type == '11'):
                propias_exenta = 0.0
                venta_no_sujeta = 0.0
                venta_local = 0.0
                venta_exportacion = 0.0
                iva_13 = 0.0
                retencion_1 = 0.0
                propina = 0.0
                imp_turismo = 0.0
                total_ventas = 0.0

                for l in invoice.invoice_line_ids:
                    if company_id.currency_id != l.currency_id:
                        precio = l.currency_id._convert(l.price_total, company_id.currency_id, company_id,invoice.invoice_date)
                    else:
                        precio = l.price_total

                    taxes = l.tax_ids.compute_all(l.price_unit, company_id.currency_id, l.quantity, l.product_id,invoice.partner_id)
                    for tax in taxes['taxes']:
                        imp = self.env['account.tax'].browse(tax['id'])
                        if 'exento' in imp.name.lower():
                            propias_exenta += precio
                        if 'retención de iva' in imp.name.lower() or 'gran contribuyente' in imp.name.lower():
                            subprecio = tax['amount']
                            if company_id.currency_id != l.currency_id:
                                subprecio = l.currency_id._convert(subprecio, company_id.currency_id, company_id,invoice.invoice_date)
                                retencion_1 += subprecio
                            else:
                                retencion_1 += subprecio
                        if not 'exento' in imp.name.lower():
                            if 'consumidor final' in imp.name.lower() or 'consumidores finales' in imp.name.lower():
                                if l.partner_id.country_id.name == 'El Salvador':
                                    pre_grab = tax['base']
                                    if company_id.currency_id != l.currency_id:
                                        pre_grab = l.currency_id._convert(pre_grab, company_id.currency_id, company_id,invoice.invoice_date)
                                        iva = l.currency_id._convert(tax['amount'], company_id.currency_id, company_id,invoice.invoice_date)
                                        venta_local += pre_grab
                                        venta_local += iva
                                    else:
                                        venta_local += pre_grab
                                        venta_local += tax['amount']
                                else:
                                    pre_deb = tax['base']
                                    if company_id.currency_id != l.currency_id:
                                        pre_deb = l.currency_id._convert(pre_deb, company_id.currency_id, company_id, invoice.invoice_date)
                                        iva = l.currency_id._convert(tax['amount'], company_id.currency_id, company_id,invoice.invoice_date)
                                        # venta_exportacion += pre_deb
                                        venta_local += pre_deb
                                        venta_local += iva
                                    else:
                                        # venta_exportacion += pre_deb
                                        venta_local += pre_deb
                                        venta_local += tax['amount']
                            if 'turismo' in imp.name.lower():
                                subprecio = tax['amount']
                                if company_id.currency_id != l.currency_id:
                                    subprecio = l.currency_id._convert(subprecio, company_id.currency_id, company_id,invoice.invoice_date)
                                    imp_turismo += subprecio
                                else:
                                    imp_turismo += subprecio

                    if not l.tax_ids:
                        if l.product_id and ('propinas' in l.product_id.name.lower()):
                            propina += precio
                        else:
                            venta_no_sujeta += precio
                if company_id.currency_id != l.currency_id:
                    total = invoice.currency_id._convert(invoice.amount_total, company_id.currency_id, company_id,invoice.invoice_date)
                    total_ventas += total
                else:
                    total_ventas += invoice.amount_total

                # total_ventas = propias_exenta+venta_no_sujeta+venta_local+venta_exportacion+iva_13+abs(retencion_1)+propina+imp_turismo
                linea = {
                    'fecha_emision': self.char_to_date(invoice.date_certification) if invoice.date_certification else False,
                    'numero_documento': invoice.numero_control if invoice.numero_control else '',
                    'nombre_cliente': invoice.partner_id.name or '',
                    'propias_exenta': propias_exenta,
                    'venta_no_sujeta': venta_no_sujeta,
                    'venta_local':  venta_local,
                    'venta_exportacion':  venta_exportacion,
                    'iva_13':  iva_13,
                    'retencion_1': abs(retencion_1),
                    'cuenta_terceros': 0.00,
                    'propina': propina,
                    'imp_turismo': imp_turismo,
                    'total':  total_ventas,
                }
                result.append(linea)
                f_propias_exenta += propias_exenta
                f_venta_no_sujeta += venta_no_sujeta
                f_venta_local += venta_local
                f_venta_exportacion += venta_exportacion
                f_iva_13 += iva_13
                f_retencion_1 += retencion_1
                f_propina += propina
                f_imp_turismo += imp_turismo
                f_total_ventas += total_ventas
            totales = {
                'f_propias_exenta': f_propias_exenta,
                'f_venta_no_sujeta': f_venta_no_sujeta,
                'f_venta_local': f_venta_local,
                'f_venta_exportacion': f_venta_exportacion,
                'f_iva_13': f_iva_13,
                'f_retencion_1': abs(f_retencion_1),
                'f_propina': f_propina,
                'f_imp_turismo': f_imp_turismo,
                'f_total_ventas': f_total_ventas,
                'company_name': company_id.name,
                'total_terceros': 0.00,
                'giro': self.get_giro(company_id.partner_id) if company_id.partner_id else '',
            }
        return result, totales


    def get_giro(self, partner_id):
        giro = ''
        if partner_id.fe_code_activity:
            if partner_id.fe_code_activity.activity_name:
                giro = partner_id.fe_code_activity.activity_name
        return giro

    def char_to_date(self, fecha_str):
        return datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S").date()