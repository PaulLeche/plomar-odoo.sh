# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.misc import formatLang
import operator

class ReportSaleBook(models.AbstractModel):
    _name = 'report.report_ventas_compras.report_sale_book'
    _description = "Report Sale Book XLSX"

    @api.model
    def _get_report_values(self, docids, data=None):
        company_id = data.get('form', {}).get(
            'company_id', False)
        if not company_id:
            company_id = self.env.user.company_id
        else:
            company_id = self.env['res.company'].browse(company_id[0])

        date = self._get_date(data)
        data, ultima = self.generate_records(data)
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'self': self,
            'data': data,
            'ultima': ultima,
            'format_price': self._format_price,
            'company_id': company_id,
            'date': date
        }
        return docargs

    def _get_date(self, data):
        date_final = ""
        date_from = datetime.strptime(data['form']['date_from'], DEFAULT_SERVER_DATE_FORMAT).strftime("%d de %B de %Y")
        date_to = datetime.strptime(data['form']['date_to'], DEFAULT_SERVER_DATE_FORMAT).strftime("%d de %B de %Y")
        months = {'january': 'enero', 'february': 'febrero', 'march': 'marzo', 'april': 'abril', 'may': 'mayo',
                  'june': 'junio', 'july': 'julio', 'august': 'agosto', 'september': 'septiembre',
                  'november': 'noviembre', 'december': 'diciembre'}
        for k, v in months.items(): date_from = date_from.lower().replace(k, v)
        for k, v in months.items(): date_to = date_to.lower().replace(k, v)
        if date_from == date_to:
            date_final = '{}'.format(date_from).upper()
        else:
            date_final = 'Del {} al {}'.format(date_from, date_to).upper()
        return date_final

    def _format_price(self, price, currency_id):
        if not price:
            return '0.00'
        amount_f = formatLang(self.env, price, dp='Product Price',
                              currency_obj=currency_id)
        amount_f = amount_f.replace(currency_id.symbol, '').strip()
        result = amount_f.replace(',', '')
        format_final = '{0:,.2f}'.format(float(result))
        return format_final

    def generate_records(self, data):
        result = []
        if not data.get('form', False):
            return result

        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        journal_ids = data['form']['journal_ids']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        empresa = self.env['res.company'].browse(
            data['form']['company_id'][0])
        folio = data['form']['folio_inicial']

        facturas = self.env['account.move'].search([
            ('state', 'in', ['posted', 'cancel']),
            ('journal_id', 'in', journal_ids),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('company_id', '=', empresa.id)], order='date,name')

        establecimientos = ", ".join([jou.name for jou in self.env['account.journal'].browse(journal_ids)])

        # CURRENCY FROM WIZARD
        company_currency_id = self.env['res.currency'].browse(
            data['form']['currency_id'][0])

        # NUMBER OF MOVES
        no = 0
        
        # NUMBER OF INVOICE PER COMPANY
        final_dict = {}
        company_fac_total = {}
        company_fac_total_final = {}

        # TOTAL VALUES
        total_bienes_gravados = 0.00
        total_servicios_gravados = 0.00
        total_bienes_exentos = 0.00
        total_servicios_exentos = 0.00

        # TOTAL FINAL
        total_iva_final = 0.00
        total_subtotal_final = 0.00

        if facturas:
            for inv in facturas:
                no += 1
                move_name = inv.name

                # ELIMINAR CUANDO SE INSTALE EL CERTIFICADOR
                fel_serie = inv.fe_serie if inv.fe_serie else ""
                fel_no = inv.fe_number if inv.fe_number else ""

                date = inv.invoice_date if inv.invoice_date else inv.date

                # OTHER INVOICE DATA
                tipo = 'NC' if inv.move_type == 'in_refund' or inv.move_type == 'out_refund' else inv.journal_id.fe_type 
                # tipo = 'NC' if inv.move_type == 'in_refund' or inv.move_type == 'out_refund' else 'FC'

                # ELIMINAR CUANDO SE INSTALE EL CERTIFICADOR
                if inv.state in ['posted']:
                    # AMOUNT PER INVOICE
                    bienes_gravados = 0.00
                    servicios_gravados = 0.00
                    bienes_exentos = 0.00
                    servicios_exentos = 0.00

                    # TAXES AND TOTALS 
                    amount_total = 0.00
                    iva_total = 0.00
                    total_iva_inv = 0.00
                    total_isr_inv = 0.00

                    # GET INVOICE NUMBER FOR EVERY PARTNER
                    partner = inv.partner_id.name
                    if partner in company_fac_total:
                        company_fac_total[partner][0] += 1
                        company_fac_total[partner][1] += ( inv.amount_total ) * (-1) if inv.move_type == 'in_refund' or inv.move_type == 'out_refund' else inv.amount_total
                    else:
                        company_fac_total[partner] = [1, ( inv.amount_total ) * (-1) if inv.move_type == 'in_refund' or inv.move_type == 'out_refund' else inv.amount_total, inv.partner_id.vat or "C/F"]
                    
                    for line in inv.invoice_line_ids:
                        iva_line = 0.00
                        isr_line = 0.00
                        total_price_line = 0.00
                        price_total = 0.00

                        # GET PRICES 
                        if inv.currency_id == company_currency_id:
                            total_price_line += line.price_subtotal
                        else:
                            total_price_line += line.currency_id._convert(line.price_subtotal, line.company_id.currency_id, line.company_id, line.date)

                        # GET TAXES 
                        taxes = line.tax_ids.compute_all(
                            line.price_unit, empresa.currency_id, line.quantity,
                            line.product_id, inv.partner_id)

                        for tax in taxes['taxes']:
                            if 'IVA' in tax['name']:
                                if inv.currency_id == company_currency_id:
                                    iva_line = tax['amount'] 
                                else:
                                    iva_line = line.currency_id._convert(tax['amount'], line.company_id.currency_id, line.company_id, line.date)
                                    
                                total_iva_inv += iva_line 

                            if 'ISR' in tax['name']:
                                if inv.currency_id == company_currency_id:
                                    isr_line = tax['amount'] 
                                else:
                                    isr_line = line.currency_id._convert(tax['amount'], line.company_id.currency_id, line.company_id, line.date)

                                total_isr_inv += isr_line 

                        # GET AMOUNT UNTAXED AND PRICE TOTAL WITH TAXES
                        if inv.move_type == 'in_refund' or inv.move_type == 'out_refund':
                            amount_untaxed = ( inv.amount_untaxed ) * (-1) if inv.currency_id == company_currency_id else ( inv.amount_untaxed_signed ) * (-1)
                            price_total = ( total_price_line ) * (-1) 
                            total_iva_inv = total_iva_inv * (-1)
                        else:
                            amount_untaxed = inv.amount_untaxed if inv.currency_id == company_currency_id else inv.amount_untaxed_signed
                            price_total = total_price_line 

                        # GET VALUES OF LINES 
                        if line.tipo_gasto == "compra":
                            if line.price_subtotal != line.price_total:
                                bienes_gravados += price_total
                            else:
                                bienes_exentos += price_total

                        elif line.tipo_gasto == "servicio":
                            if line.price_subtotal != line.price_total:
                                servicios_gravados += price_total
                            else:
                                servicios_exentos += price_total

                    # IVA AND AMOUNT TOTAL
                    if inv.move_type == 'in_refund' or inv.move_type == 'out_refund':
                        amount_total = ( inv.amount_tax + inv.amount_untaxed - total_isr_inv ) * (-1) if inv.currency_id == company_currency_id else ( inv.amount_tax_signed + inv.amount_untaxed_signed - total_isr_inv ) * (-1)
                    else:
                        amount_total = inv.amount_tax + inv.amount_untaxed - total_isr_inv if inv.currency_id == company_currency_id else inv.amount_tax_signed + inv.amount_untaxed_signed - total_isr_inv
                    iva_total = amount_total - amount_untaxed

                    # SUM TOTAL VALUES 
                    total_bienes_gravados += bienes_gravados
                    total_servicios_gravados += servicios_gravados
                    total_bienes_exentos += bienes_exentos
                    total_servicios_exentos += servicios_exentos

                    # TOTAL FINAL
                    total_iva_final += iva_total
                    total_subtotal_final += amount_total if inv.currency_id == company_currency_id else inv.amount_total_signed

                    linea = {
                        'no': no,
                        'move_name': move_name,
                        'company': empresa.name.encode('ascii', 'ignore') or "",
                        'nit': empresa.vat or "",
                        'direccion': empresa.street.encode('ascii', 'ignore'),
                        'folio_no': int(folio),
                        'establecimientos': establecimientos,
                        'fecha': datetime.strptime(
                            str(date),
                            DEFAULT_SERVER_DATE_FORMAT).strftime(date_format),
                        'tipo': tipo,
                        'serie': fel_serie,
                        'numero': fel_no,
                        'nit_cliente': inv.partner_id.vat or "C/F",
                        'cliente': partner or '',
                        'bienes_gravados': bienes_gravados,
                        'servicios_gravados': servicios_gravados,
                        'bienes_exentos': bienes_exentos,
                        'servicios_exentos': servicios_exentos,
                        'iva': iva_total,
                        'subtotal': amount_total if inv.currency_id == company_currency_id else inv.amount_total_signed,
                    }
                else:
                    linea = {
                        'no': no,
                        'move_name': move_name,
                        'company': empresa.name.encode('ascii', 'ignore') or "",
                        'nit': empresa.vat or "",
                        'direccion': empresa.street.encode('ascii', 'ignore'),
                        'folio_no': int(folio),
                        'establecimientos': establecimientos,
                        'fecha': datetime.strptime(
                            str(date),
                            DEFAULT_SERVER_DATE_FORMAT).strftime(date_format),
                        'tipo': tipo,
                        'serie': fel_serie,
                        'numero': fel_no,
                        'nit_cliente': '***ANULADA***',
                        'cliente': '***FACTURA ANULADA***',
                        'bienes_gravados': 0.00,
                        'servicios_gravados': 0.00,
                        'bienes_exentos': 0.00,
                        'servicios_exentos': 0.00,
                        'iva': 0.00,
                        'subtotal': 0.00,
                    }

                result.append(linea)

            # ORDER DICT WITH MOVE AMOUNT
            for dict_item in company_fac_total:
                company_fac_total_final[dict_item] = company_fac_total[dict_item][1]

            partner_sort = sorted(company_fac_total_final.items(), key=operator.itemgetter(1), reverse=True)
            
            for partner in enumerate(partner_sort):
                final_dict[partner[1][0]] = company_fac_total[partner[1][0]]

            # TOTALS 
            linea = {
                'cliente': "Totales",
                'company_fac_total': final_dict,
                'total_bienes_gravados': total_bienes_gravados,
                'total_servicios_gravados': total_servicios_gravados,
                'total_bienes_exentos': total_bienes_exentos,
                'total_servicios_exentos': total_servicios_exentos,

                'total_no_fac': no,
                'total_iva_final': total_iva_final,
                'total_subtotal_final': total_subtotal_final,
            }

            # split in folios
            results = []
            folio = 1
            i = 1
            rows = []
            for row in result:
                rows.append(row)
                if i == 22:
                    results.append([folio, rows])
                    rows = []
                    i = 1
                    folio += 1
                else:
                    i += 1
            if len(rows) > 0:
                results.append([folio, rows])
            return results, linea
