# -*- encoding: utf-8 -*-

from odoo.tools.translate import _
from odoo import fields, models, api
from datetime import datetime, time
import json
from dateutil.relativedelta import relativedelta
from odoo.tools import float_round

class ReportTaxpayer(models.AbstractModel):
    _name = 'report.advanced_reports.report_purchase'
    _description = 'report advanced_reports report_purchase'

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
            date_from_m = self._month_letters(docs.date_from.month)
            date_to_m = self._month_letters(docs.date_to.month)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'self': self,
            'data': result,
            'ultima': totales,
            'date_from': date_from,
            'date_to': date_to,
            'date_from_m': date_from_m,
            'date_to_m': date_to_m,
        }
        return docargs

    def generate_records(self, record_ids):
        result = []
        totales = []
        f_propias_exenta = 0.0
        f_locales_propias = 0.0
        f_propias_grabada = 0.0
        f_credito_fiscal = 0.0
        f_imp_exentas = 0.0
        f_imp_grabadas = 0.0
        f_imp_poliza = 0.0
        f_percepcion_1 = 0.0
        f_anticipo_2 = 0.0
        f_total_compras = 0.0
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
            ('move_type', 'in', ['in_invoice']),
            ('fe_type', 'in', ['03', '14']),
            ('company_id', '=', company_id.id)], order='date,name')
        if invoices:
            for invoice in invoices:
                propias_exenta = 0.0
                locales_propias = 0.0
                propias_grabada = 0.0
                credito_fiscal = 0.0
                imp_exentas = 0.0
                imp_grabadas = 0.0
                imp_poliza = 0.0
                percepcion_1 = 0.0
                anticipo_2 = 0.0
                f_sujetos_excluidos = 0.0
                total_compras = 0.0
                sujetos_ex = False
                if invoice.fe_type == '14':
                    sujetos_ex = True
                for l in invoice.invoice_line_ids:
                    if company_id.currency_id != l.currency_id:
                        precio_sub = l.currency_id._convert(l.price_subtotal, company_id.currency_id, company_id,invoice.invoice_date)
                        precio = l.currency_id._convert(l.price_total, company_id.currency_id, company_id,invoice.invoice_date)
                    else:
                        precio_sub = l.price_subtotal
                        precio = l.price_total
                    price = precio_sub
                    # if l.partner_id.type_consumer_taxp == 'consumer' and not l.partner_id.nrc:
                    #     sujetos_excluidos = precio
                    # else:
                    #     sujetos_excluidos = 0.0
                    if sujetos_ex == True:
                        sujetos_excluidos = precio_sub
                    else:
                        sujetos_excluidos = 0.0
                    taxes = l.tax_ids.compute_all(l.price_unit, company_id.currency_id, l.quantity, l.product_id, invoice.partner_id)
                    propias_grabada_ini = 0.0
                    if sujetos_ex == False:
                        for tax in taxes['taxes']:
                            imp = self.env['account.tax'].browse(tax['id'])
                            if 'exento' in imp.name.lower():
                                propias_exenta += precio
                                if l.partner_id.country_id.name != 'El Salvador':
                                    imp_exentas += precio

                            if 'no sujeto' in imp.name.lower():
                                locales_propias += precio
                            if imp.amount == 13 or 'iva por cobrar' in imp.name.lower():
                                if company_id.currency_id == l.currency_id:
                                    if l.partner_id.country_id.name == 'El Salvador':
                                        if propias_grabada_ini == 0.0:
                                            # propias_grabada_ini += tax['base']
                                            propias_grabada_ini += precio
                                        credito_fiscal += tax['amount']
                                    else:
                                        # imp_grabadas += tax['base']
                                        imp_grabadas += precio
                                        imp_poliza += tax['amount']
                                else:
                                    if l.partner_id.country_id.name == 'El Salvador':
                                        if propias_grabada_ini == 0.0:
                                            # propias_grabada_ini += l.currency_id._convert(tax['base'], company_id.currency_id, company_id,invoice.invoice_date)
                                            propias_grabada_ini += precio
                                        credito_fiscal += l.currency_id._convert(tax['amount'], company_id.currency_id,company_id, invoice.invoice_date)
                                    else:
                                        if propias_grabada_ini == 0.0:
                                            # propias_grabada_ini += l.currency_id._convert(tax['base'], company_id.currency_id,company_id, invoice.invoice_date)
                                            propias_grabada_ini += precio
                                        credito_fiscal += l.currency_id._convert(tax['amount'], company_id.currency_id,company_id, invoice.invoice_date)

                            if imp.amount == 2 and 'anticipo a cuenta' in imp.name.lower():
                                if company_id.currency_id == l.currency_id:
                                    if l.partner_id.country_id.name == 'El Salvador':
                                        if propias_grabada_ini == 0.0:
                                            # propias_grabada += tax['base']
                                            propias_grabada_ini += precio
                                        anticipo_2 += tax['amount']
                                    else:
                                        # imp_grabadas += tax['base']
                                        imp_grabadas += precio
                                        anticipo_2 += tax['amount']
                                else:
                                    if l.partner_id.country_id.name == 'El Salvador':
                                        if propias_grabada_ini == 0.0:
                                            # propias_grabada_ini += l.currency_id._convert(tax['base'], company_id.currency_id,company_id, invoice.invoice_date)
                                            propias_grabada_ini += precio
                                        anticipo_2 += l.currency_id._convert(tax['amount'], company_id.currency_id,company_id, invoice.invoice_date)
                                    else:
                                        if propias_grabada_ini == 0.0:
                                            # propias_grabada_ini += l.currency_id._convert(tax['base'], company_id.currency_id,company_id, invoice.invoice_date)
                                            propias_grabada_ini += precio
                                        anticipo_2 += l.currency_id._convert(tax['amount'], company_id.currency_id,company_id, invoice.invoice_date)

                            if imp.amount == 1 and 'percepción de iva' in imp.name.lower():
                                if company_id.currency_id == l.currency_id:
                                    if l.partner_id.country_id.name == 'El Salvador':
                                        if propias_grabada_ini == 0.0:
                                            # propias_grabada_ini += tax['base']
                                            propias_grabada_ini += precio
                                        percepcion_1 += tax['amount']
                                    else:
                                        # imp_grabadas += tax['base']
                                        imp_grabadas += precio
                                        percepcion_1 += tax['amount']
                                else:
                                    if l.partner_id.country_id.name == 'El Salvador':
                                        if propias_grabada_ini == 0.0:
                                            # propias_grabada_ini += l.currency_id._convert(tax['base'], company_id.currency_id,company_id, invoice.invoice_date)
                                            propias_grabada_ini += precio
                                        percepcion_1 += l.currency_id._convert(tax['amount'], company_id.currency_id, company_id,invoice.invoice_date)
                                    else:
                                        if propias_grabada_ini == 0.0:
                                            # propias_grabada_ini += l.currency_id._convert(tax['base'], company_id.currency_id,company_id, invoice.invoice_date)
                                            propias_grabada_ini += precio
                                        percepcion_1 += l.currency_id._convert(tax['amount'], company_id.currency_id,company_id, invoice.invoice_date)

                    propias_grabada += propias_grabada_ini

                if company_id.currency_id != l.currency_id:
                    total = invoice.currency_id._convert(invoice.amount_total, company_id.currency_id, company_id,invoice.invoice_date)
                    total_compras += total
                else:
                    total_compras += invoice.amount_total
                if invoice.document_number:
                    numero_documento = invoice.document_number
                else:
                    if invoice.uuid_code:
                        numero_documento = invoice.uuid_code
                    else:
                        numero_documento = ''

                linea = {
                    'numero_documento': numero_documento,
                    'fecha_emision': self.char_to_date(invoice.date_certification) if invoice.date_certification else False,
                    'nro_registro':  self.get_nrc_dui_partner(invoice.partner_id),
                    'nombre_cliente': invoice.partner_id.name or '',
                    'propias_exenta': propias_exenta,
                    'locales_propias': locales_propias,
                    'propias_grabada': propias_grabada,
                    'credito_fiscal': credito_fiscal,
                    'imp_exentas': imp_exentas,
                    'imp_grabadas': imp_grabadas,
                    'imp_poliza': imp_poliza,
                    'percepcion_1': percepcion_1,
                    'anticipo_2': anticipo_2,
                    'sujetos_excluidos': sujetos_excluidos,
                    'total_compras': total_compras
                }
                result.append(linea)
                f_propias_exenta += propias_exenta
                f_locales_propias += locales_propias
                f_propias_grabada += propias_grabada
                f_credito_fiscal += credito_fiscal
                f_imp_exentas += imp_exentas
                f_imp_grabadas += imp_grabadas
                f_imp_poliza += imp_poliza
                f_percepcion_1 += percepcion_1
                f_anticipo_2 += anticipo_2
                f_sujetos_excluidos += sujetos_excluidos
                f_total_compras += total_compras
            totales = {
                'f_propias_exenta': f_propias_exenta,
                'f_locales_propias': f_locales_propias,
                'f_propias_grabada': f_propias_grabada,
                'f_credito_fiscal': f_credito_fiscal,
                'f_imp_exentas': f_imp_exentas,
                'f_imp_grabadas': f_imp_grabadas,
                'f_imp_poliza': f_imp_poliza,
                'f_percepcion_1': f_percepcion_1,
                'f_anticipo_2': f_anticipo_2,
                'f_sujetos_excluidos': f_sujetos_excluidos,
                'f_total_compras': f_total_compras,
                'company_name': company_id.name,
                'giro': self.get_giro(company_id.partner_id) if company_id.partner_id else '',
            }
        return result, totales

    # def insert_dash_before_last_nrc(self, nrc):
    #     if len(nrc) > 1:
    #         return nrc[:-1] + '-' + nrc[-1]
    #     return nrc
    def get_giro(self, partner_id):
        giro = ''
        if partner_id.fe_code_activity:
            if partner_id.fe_code_activity.activity_name:
                giro = partner_id.fe_code_activity.activity_name
        return giro

    def get_nrc_dui_partner(self, partner_id):
        nro_registro = ''
        if partner_id:
            if partner_id.type_consumer_taxp == 'consumer':
                if partner_id.dui_field:
                    nro_registro = partner_id.dui_field
            else:
                if partner_id.nrc:
                    nro_registro = partner_id.nrc
        return nro_registro

    def char_to_date(self, fecha_str):
        return datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S").date()

