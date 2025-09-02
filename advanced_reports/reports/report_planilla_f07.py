# -*- encoding: utf-8 -*-

from odoo.tools.translate import _
from odoo import fields, models, api
import json
from dateutil.relativedelta import relativedelta
from odoo.tools import float_round
from datetime import datetime, time

class ReportPlanillaF07(models.AbstractModel):
    _name = 'report.advanced_reports.report_planilla_f07'
    _description = 'report advanced_reports report_planilla_f07'


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
    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     result, totales = self.generate_records(data)
    #     model = self.env.context.get('active_model')
    #     docs = self.env[model].browse(self.env.context.get('active_id'))
    #     if docs:
    #         date_from = self._get_format_date(docs.date_from)
    #         date_to = self._get_format_date(docs.date_to)
    #     docargs = {
    #         'doc_ids': self.ids,
    #         'doc_model': model,
    #         'docs': docs,
    #         'self': self,
    #         'data': result,
    #         'ultima': totales,
    #         'date_from': date_from,
    #         'date_to': date_to,
    #     }
    #     return docargs

    def generate_records1(self, record_ids):
        result = []
        totales = []
        date_from = record_ids.date_from
        date_to = record_ids.date_to
        # Convertirlas a datetime con hora mínima y máxima
        start_datetime = datetime.combine(date_from, time.min)  # 00:00:00
        end_datetime = datetime.combine(date_to, time.max).replace(microsecond=0)  # 23:59:59
        # Convertir a string en formato requerido
        date_from_str = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
        date_to_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        company_id = record_ids.company_id
        moves = self.env['account.move'].search([('move_type', 'in', ['out_invoice']),
                                                 ('state', '=', 'posted'),
                                                 ('date_certification', '>=', date_from_str),
                                                 ('date_certification', '<=', date_to_str),
                                                 ('company_id', '=', company_id.id)], order = 'date,name')

        if moves:
            for move in moves:
                swich = False
                type = move.fe_type
                fe_type = self.get_type_document(type)
                if move.number_internal_control:
                    if move.class_of_document == 4:
                        numero_control = ''
                    else:
                        numero_control = move.number_internal_control
                else:
                    numero_control = ''

                # nrc = self.get_nrc(move)
                ventas_exentas = 0.0
                ventas_no_sujetas = 0.0
                ventas_gravadas = 0.0
                ventas_grabadas_locales = 0.0
                cuenta_terceros = 0.0
                deb_cuenta_terceros = 0.0
                gran_contribuyente = 0.0
                propina = 0.0
                imp_turismo = 0.0
                for l in move.invoice_line_ids:
                    if not (l.product_id and ('propinas' in l.product_id.name.lower())):
                        if l.tax_ids:
                            taxes = l.tax_ids.compute_all(l.price_unit, company_id.currency_id, l.quantity, l.product_id, move.partner_id)
                            for tax in taxes['taxes']:
                                # imp = self.env['account.tax'].browse(tax['id'])
                                if 'exento iva ventas' in tax['name'].lower():
                                    ventas_exentas += l.price_subtotal
                                elif 'iva por pagar contribuyentes' in tax['name'].lower():
                                    ventas_gravadas += l.price_subtotal
                                    ventas_gravadas += tax['amount']
                                elif 'imp. ventas a cuenta de terceros no domiciliados' in tax['name'].lower():
                                    cuenta_terceros += l.price_subtotal
                                    deb_cuenta_terceros += tax['amount']
                                elif 'impuesto por venta terceros' in tax['name'].lower():
                                    swich = True
                                elif 'retención de iva' in tax['name'].lower():
                                    swich = True
                                elif 'iva por pagar consumidores finales' in tax['name'].lower():
                                    swich = True
                                elif 'gran contribuyente' in tax['name'].lower():
                                    gran_contribuyente += tax['amount']
                                elif 'turismo' in tax['name'].lower():
                                    imp_turismo += tax['amount']
                        else:
                            ventas_no_sujetas += l.price_subtotal
                    else:
                        propina += l.price_subtotal

                dui, nrc = self.get_dui_nrc(move)
                nrc = self.insert_dash_before_last_nrc(nrc)

                # if move.partner_id and move.partner_id.type_consumer_taxp == 'taxpayer' and swich == False:
                if move.fe_type == '03' and swich == False:
                    line1 = {
                        'fecha_fact': self.char_to_date(move.date_certification) if move.date_certification else False,
                        'clase_doc': move.class_of_document if move.class_of_document else 0,
                        'tipo_doc_emitido': type,
                        'numero_resol': move.number_of_resolution if move.number_of_resolution else '',
                        'serie': move.number_of_series_document if move.number_of_series_document else 0,
                        'correlativo': move.uuid_code.replace("-", "") if move.uuid_code else '',
                        'numero_control': numero_control,
                        'nrc': nrc,
                        'cliente': move.partner_id.name if move.partner_id else '',
                        'ventas_exentas': ventas_exentas,
                        'ventas_no_sujetas': ventas_no_sujetas,
                        'ventas_gravadas': ventas_gravadas,
                        'ventas_grabadas_locales': ventas_grabadas_locales,
                        'venta_cuenta_terceros': cuenta_terceros,
                        'deb_cuenta_terceros': deb_cuenta_terceros,
                        'propina': propina,
                        'imp_turismo': imp_turismo,
                        'total': (ventas_exentas+ventas_no_sujetas+ventas_gravadas+ventas_grabadas_locales+cuenta_terceros+deb_cuenta_terceros+propina+imp_turismo) - gran_contribuyente or 0.0,
                        'dui': dui,
                        'tipo_operacion': move.type_rental_operation if move.type_rental_operation else '',
                        'tipo_ingreso': move.type_rental_income if move.type_rental_income else '',
                        'anex': move.number_of_annexed_1 if move.number_of_annexed_1 else 0,
                    }
                    result.append(line1)
        return result, totales

    def generate_records2(self, record_ids):
        result = []
        totales = []
        date_from = record_ids.date_from
        date_to = record_ids.date_to
        start_datetime = datetime.combine(date_from, time.min)  # 00:00:00
        end_datetime = datetime.combine(date_to, time.max).replace(microsecond=0)  # 23:59:59
        date_from_str = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
        date_to_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        company_id = record_ids.company_id
        moves = self.env['account.move'].search([('move_type', 'in', ['out_invoice']),
                                                 ('state', '=', 'posted'),
                                                 ('date_certification', '>=', date_from_str),
                                                 ('date_certification', '<=', date_to_str),
                                                 ('company_id', '=', company_id.id)], order='date,name')

        if moves:
            dict_uuid_code = {}
            for move in moves:
                impuesto = False
                tipo_doc = self.get_type_document(move.fe_type)
                ventas_exentas = 0.0
                internas_exentas = 0.0
                ventas_no_sujetas = 0.0
                ventas_grabadas_locales = 0.0
                exportaciones_centroamericana_int = 0.0
                exportaciones_centroamericana_ext = 0.0
                exportaciones_servicio = 0.0
                zonas_francas = 0.0
                terceros_domiciliados = 0.0
                propina = 0.0
                imp_turismo = 0.0

                for line in move.invoice_line_ids:
                    if not (line.product_id and ('propinas' in line.product_id.name.lower())):
                        if line.tax_ids:
                            taxes = line.tax_ids.compute_all(line.price_unit, company_id.currency_id, line.quantity, line.product_id,move.partner_id)
                            for tax in taxes['taxes']:
                                if 'exento iva ventas' in tax['name'].lower():
                                    ventas_exentas += line.price_subtotal
                                elif 'exento no sujeto a proporcionalidad' in tax['name'].lower():
                                    internas_exentas += line.price_subtotal
                                elif 'iva por pagar consumidores finales' in tax['name'].lower():
                                    ventas_grabadas_locales += line.price_subtotal
                                    ventas_grabadas_locales += tax['amount']
                                # elif 'turismo' not in tax['name'].lower():
                                #     ventas_grabadas_locales += tax['amount']
                                # elif 'turismo' in tax['name'].lower():
                                #     ventas_no_sujetas += tax['amount']
                                elif 'exportaciones dentro del area centroamericana' in tax['name'].lower():
                                    exportaciones_centroamericana_int += line.price_subtotal
                                elif 'exportaciones fuera de area centroamericana' in tax['name'].lower():
                                    exportaciones_centroamericana_ext += line.price_subtotal
                                elif 'exportaciones de servicios' in tax['name'].lower():
                                    exportaciones_servicio += line.price_subtotal
                                elif 'ventas a zonas francas y dpa' in tax['name'].lower():
                                    zonas_francas += line.price_subtotal
                                elif 'imp. ventas a cuenta de terceros no domiciliados' in tax['name'].lower():
                                    terceros_domiciliados += line.price_subtotal
                                elif 'impuesto por venta terceros' in tax['name'].lower():
                                    impuesto = True
                                elif 'retención de iva' in tax['name'].lower():
                                    impuesto = True
                                elif 'turismo' in tax['name'].lower():
                                    imp_turismo += tax['amount']
                        else:
                            ventas_no_sujetas += line.price_total
                    else:
                        propina += line.price_subtotal

                if move.partner_id and move.partner_id.type_consumer_taxp == 'consumer' and impuesto == False:
                    date_certification = self.char_to_date(move.date_certification) if move.date_certification else False
                    if date_certification and move.numero_control and move.uuid_code:
                        uuid_code_list = dict_uuid_code.setdefault(date_certification,[])
                        uuid_code_list.append((move.numero_control, move.uuid_code))

                    line2 = {
                        'fecha': date_certification,
                        'clase_doc': move.class_of_document if move.class_of_document else 0,
                        'tipo_doc': tipo_doc,
                        'num_resolucion': move.number_of_resolution if move.number_of_resolution else '',
                        'serie_doc': move.number_of_series_document if move.number_of_series_document else 0,
                        'control_interno_del': move.numero_control if move.numero_control else '',
                        'control_interno_al': move.numero_control if move.numero_control else '',
                        'numero_documento_del': move.uuid_code if move.uuid_code else '',
                        'numero_documento_al': move.uuid_code if move.uuid_code else '',
                        'maq_registradora': '',
                        'ventas_exentas': ventas_exentas, # los que tienen impuesto iva venta
                        'internas_exentas': internas_exentas,
                        'ventas_no_sujetas': ventas_no_sujetas, # Los que no tienen impuestos, producto propinas no cuenta
                        'ventas_grabadas_locales': ventas_grabadas_locales,# base iponible mas iva
                        'exportaciones_centroamericana_int': exportaciones_centroamericana_int,
                        'exportaciones_centroamericana_ext': exportaciones_centroamericana_ext,
                        'exportaciones_servicio': exportaciones_servicio,
                        'zonas_francas': zonas_francas,
                        'terceros_domiciliados': terceros_domiciliados,
                        'propina': propina,
                        'imp_turismo': imp_turismo,
                        'ventas_totales': ventas_exentas+internas_exentas+ventas_no_sujetas+ventas_grabadas_locales+exportaciones_centroamericana_int+exportaciones_centroamericana_ext+exportaciones_servicio+zonas_francas+terceros_domiciliados+propina+imp_turismo,
                        'tipo_operacion': move.type_rental_operation if move.type_rental_operation else '',
                        'tipo_ingreso': move.type_rental_income if move.type_rental_income else '',
                        'anex': move.number_of_annexed_2 if move.number_of_annexed_2 else 0,
                    }
                    result.append(line2)
            self.get_min_max_uuid_code(result, dict_uuid_code)
        return result, totales

    def generate_records3(self, record_ids):
        result = []
        totales = []
        date_from = record_ids.date_from
        date_to = record_ids.date_to
        start_datetime = datetime.combine(date_from, time.min)  # 00:00:00
        end_datetime = datetime.combine(date_to, time.max).replace(microsecond=0)  # 23:59:59
        date_from_str = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
        date_to_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        company_id = record_ids.company_id
        moves = self.env['account.move'].search([('move_type', 'in', ['in_invoice']),
                                                 ('state', '=', 'posted'),
                                                 ('date_certification', '>=', date_from_str),
                                                 ('date_certification', '<=', date_to_str),
                                                 ('company_id', '=', company_id.id),
                                                 ('fe_type', 'in', ['03', '05', '06', '11'])], order='date,name')

        if moves:
            for move in moves:
                impuesto = False
                fe_type = move.fe_type
                #tipo_doc = self.get_type_document(fe_type)
                # nrc = self.get_nrc(move)
                compras_internas_exentas = 0.0
                internaciones_exentas = 0.0
                importaciones_exentas = 0.0
                compras_internas = 0.0
                internaciones_grabadas = 0.0
                importaciones_grabadas = 0.0
                importaciones_Servicios = 0.0
                credito_fiscal = 0.0
                for l in move.invoice_line_ids:
                    if l.tax_ids:
                        taxes = l.tax_ids.compute_all(l.price_unit, company_id.currency_id, l.quantity, l.product_id, move.partner_id)
                        for tax in taxes['taxes']:
                            imp = self.env['account.tax'].browse(tax['id'])
                            if 'exento iva compras' in imp.name.lower():
                                compras_internas_exentas += l.price_subtotal
                            elif 'internaciones exentas' in imp.name.lower():
                                internaciones_exentas += l.price_subtotal
                            elif 'importaciones exentas y/o no sujetas' in imp.name.lower():
                                importaciones_exentas += l.price_subtotal
                            elif 'iva por cobrar' in imp.name.lower():
                                compras_internas += l.price_subtotal
                                credito_fiscal += tax['amount']
                            elif 'internaciones gravadas' in imp.name.lower():
                                internaciones_grabadas += l.price_subtotal
                            elif 'importaciones gravadas de bienes' in imp.name.lower():
                                importaciones_grabadas += l.price_subtotal
                            elif 'importaciones gravadas de servicios' in imp.name.lower():
                                importaciones_Servicios += l.price_subtotal
                            elif 'percepción de iva' in imp.name.lower():
                                impuesto = True
                            elif 'anticipo a cuenta' in imp.name.lower():
                                impuesto = True

                dui_proveedor, nrc = self.get_dui_nrc(move)

                # nrc = self.insert_dash_before_last_nrc(nrc)
                # if move.partner_id.identification_type == '13':
                #     if move.partner_id.nrc:
                #         dui_proveedor = ''
                #     else:
                #         if move.partner_id.dui_field:
                #             dui_proveedor = move.partner_id.dui_field
                #         else:
                #             dui_proveedor = ''
                # else:
                #     dui_proveedor = ''
                document_classification = move.document_classification
                #clasificacion_renta = self.get_document_classification(document_classification)
                type_of_operation = move.type_of_operation
                #tipo_operacion = self.get_type_of_operation(type_of_operation)
                sector = move.sector
                #sector_renta = self.get_sector(sector)
                type_of_cost_or_expense = move.type_of_cost_or_expense
                # tipo_costo = self.get_type_of_cost_or_expense(type_of_cost_or_expense)
                if move.uuid_user:
                    corralativo_doc = move.uuid_user
                else:
                    if move.document_number:
                        corralativo_doc = move.document_number
                    else:
                        corralativo_doc = ''
                if impuesto == False:
                    line3 = {
                        'fecha': self.char_to_date(move.date_certification) if move.date_certification else '',
                        'clase_doc': move.class_of_document if move.class_of_document else 0,
                        'tipo_doc': fe_type if fe_type else '',
                        'corralativo_doc': corralativo_doc,
                        'nrc': nrc,
                        'nombre_proveedor': move.partner_id.name if move.partner_id else '',
                        'compras_internas_exentas': compras_internas_exentas,
                        'internaciones_exentas': internaciones_exentas,
                        'importaciones_exentas': importaciones_exentas,
                        'compras_internas': compras_internas,
                        'internaciones_grabadas': internaciones_grabadas,
                        'importaciones_grabadas': importaciones_grabadas,
                        'importaciones_Servicios': importaciones_Servicios,
                        'credito_fiscal': credito_fiscal,
                        'total_compras': move.amount_total if move.amount_total else 0.0,
                        'dui_proveedor': dui_proveedor,
                        'tipo_operacion': type_of_operation if type_of_operation else '',
                        'clasificacion_renta': document_classification if document_classification else '',
                        'sector_renta': sector if sector else '',
                        'tipo_costo': type_of_cost_or_expense if type_of_cost_or_expense else '',
                        'anex': move.number_of_annexed_3 if move.number_of_annexed_3 else 0,
                    }
                    result.append(line3)
        return result, totales

    def generate_records4(self, record_ids):
        result = []
        totales = []
        date_from = record_ids.date_from
        date_to = record_ids.date_to
        start_datetime = datetime.combine(date_from, time.min)  # 00:00:00
        end_datetime = datetime.combine(date_to, time.max).replace(microsecond=0)  # 23:59:59
        date_from_str = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
        date_to_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        company_id = record_ids.company_id
        moves = self.env['account.move'].search([('move_type', 'in', ['out_invoice']),
                                                 ('state', '=', 'posted'),
                                                 ('date_certification', '>=', date_from_str),
                                                 ('date_certification', '<=', date_to_str),
                                                 ('company_id', '=', company_id.id)], order='date,name')

        if moves:
            # moves_filtered = [move for move in moves if any('impuesto por venta terceros' in tax.name.lower() for line in move.invoice_line_ids for tax in line.tax_ids)]
            for move in moves:
                impuesto = False
                # nrc = self.get_nrc(move)
                dui, nrc = self.get_dui_nrc(move)
                nrc = self.insert_dash_before_last_nrc(nrc)
                tipo_documento = self.get_type_document(move.fe_type)
                monto_venta = 0.0
                debito_fiscal = 0.0
                for l in move.invoice_line_ids:
                    if l.tax_ids:
                        taxes = l.tax_ids.compute_all(l.price_unit, company_id.currency_id, l.quantity, l.product_id, move.partner_id)
                        for tax in taxes['taxes']:
                            imp = self.env['account.tax'].browse(tax['id'])
                            if 'impuesto por venta terceros' in imp.name.lower():
                                monto_venta += l.price_subtotal
                                debito_fiscal += tax['amount']
                                impuesto = True
                # if not move.partner_id.nrc:
                #     if move.partner_id.identification_type == '13':
                #         dui = move.partner_id.dui_field
                #     else:
                #         dui = ''
                # else:
                #     dui = ''

                if impuesto == True:
                    line4 = {
                        'nrc': nrc,
                        'nombre_mandante': move.partner_id.name if move.partner_id else '',
                        'fecha_ccf':  self.char_to_date(move.date_certification) if move.date_certification else False,
                        'tipo_documento': tipo_documento,
                        'serie_ccf': move.number_of_series_document if move.number_of_series_document else 0,
                        'resolucion_ccf': move.number_of_resolution if move.number_of_resolution else '',
                        'numero_ccf': move.uuid_code.replace("-", "") if move.uuid_code else '',
                        'monto_venta': monto_venta,
                        'debito_fiscal': debito_fiscal,
                        'comprobante_liquidacion': '0' if move.series_of_voucher_of_liquidation else '0',
                        'resolucion_comprobante': '0' if move.resolution_of_voucher_of_liquidation else '0',
                        'numero_comprobante': '0' if move.number_of_issue_voucher_of_liquidation else '0',
                        'fecha_comprobante': '0' if move.date_of_issue_voucher_of_liquidation else '0',
                        'dui': dui,
                        'anex': move.number_of_annexed_4 if move.number_of_annexed_4 else 0,

                    }
                    result.append(line4)

        return result, totales

    def generate_records5(self, record_ids):
        result = []
        totales = []
        date_from = record_ids.date_from
        date_to = record_ids.date_to
        start_datetime = datetime.combine(date_from, time.min)  # 00:00:00
        end_datetime = datetime.combine(date_to, time.max).replace(microsecond=0)  # 23:59:59
        date_from_str = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
        date_to_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        company_id = record_ids.company_id
        moves = self.env['account.move'].search([('move_type', 'in', ['in_invoice']),
                                                 ('state', '=', 'posted'),
                                                 ('date_certification', '>=', date_from_str),
                                                 ('date_certification', '<=', date_to_str),
                                                 ('fe_type', '=', '14'),
                                                 ('company_id', '=', company_id.id)], order='date,name')

        if moves:
            for move in moves:
                tipo_doc, number_doc = self.get_number_name_document(move.partner_id)
                iva_13 = 0.0
                for l in move.invoice_line_ids:
                    if l.tax_ids:
                        taxes = l.tax_ids.compute_all(l.price_unit, company_id.currency_id, l.quantity, l.product_id, move.partner_id)
                        for tax in taxes['taxes']:
                            imp = self.env['account.tax'].browse(tax['id'])
                            if 'iva por cobrar' in imp.name.lower():
                                iva_13 += tax['amount']

                monto_compra = move.amount_untaxed

                type_of_operation = move.type_of_operation
                # operacion_renta = self.get_type_of_operation(type_of_operation)
                document_classification = move.document_classification
                # clasificacion_renta = self.get_document_classification(document_classification)
                sector = move.sector
                # sector = self.get_sector(sector)
                type_of_cost_or_expense = move.type_of_cost_or_expense
                # tipo_costo = self.get_type_of_cost_or_expense(type_of_cost_or_expense)
                line5 = {
                    'tipo_doc': tipo_doc,
                    'number_doc': number_doc if number_doc else '',
                    'nombre_proveedor': move.partner_id.name if move.partner_id else '',
                    'fecha': self.char_to_date(move.date_certification) if move.date_certification else False,
                    'serie': move.number_of_series_document if move.number_of_series_document else '',
                    'numero_doc': move.uuid_code if move.uuid_code else '',
                    'monto_compra': monto_compra,
                    'iva_13': iva_13,
                    'operacion_renta': type_of_operation if type_of_operation else '',
                    'clasificacion_renta': document_classification if document_classification else '',
                    'sector': sector if sector else '',
                    'tipo_costo': type_of_cost_or_expense if type_of_cost_or_expense else '',
                    'anex': move.number_of_annexed_5 if move.number_of_annexed_5 else 0,

                }
                result.append(line5)
        return result, totales

    def generate_records6(self, record_ids):
        result = []
        totales = []
        date_from = record_ids.date_from
        date_to = record_ids.date_to
        start_datetime = datetime.combine(date_from, time.min)  # 00:00:00
        end_datetime = datetime.combine(date_to, time.max).replace(microsecond=0)  # 23:59:59
        date_from_str = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
        date_to_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        company_id = record_ids.company_id
        moves = self.env['account.move'].search([('move_type', 'in', ['in_invoice']),
                                                 ('state', '=', 'posted'),
                                                 ('date_certification', '>=', date_from_str),
                                                 ('date_certification', '<=', date_to_str),
                                                 ('company_id', '=', company_id.id)], order='date,name')

        company_partner = company_id.partner_id
        if moves and company_partner.type_consumer_taxp == 'taxpayer' and company_partner.taxpayer_type == 'medium':
            for move in moves:
                swich = False
                nit, dui = self.get_nit_dui(move.partner_id)
                monto_sujeto = 0.0
                anticipo_2 = 0.0
                for l in move.invoice_line_ids:
                    if l.tax_ids:
                        taxes = l.tax_ids.compute_all(l.price_unit, company_id.currency_id, l.quantity, l.product_id, move.partner_id)
                        for tax in taxes['taxes']:
                            imp = self.env['account.tax'].browse(tax['id'])
                            if 'anticipo a cuenta' in imp.name.lower():
                                monto_sujeto += l.price_subtotal
                                anticipo_2 += tax['amount']
                                swich = True
                if swich == True:
                    line6 = {
                        'nit': nit,
                        'fecha_emision': self.char_to_date(move.date_certification) if move.date_certification else False,
                        'serie': move.number_of_series_document if move.number_of_series_document else 0,
                        'numero_doc': move.uuid_user if move.uuid_user else '',
                        'monto_sujeto': monto_sujeto,
                        'anticipo_2': anticipo_2,
                        'dui': dui,
                        'anex': move.number_of_annexed_6 if move.number_of_annexed_6 else 0,

                    }
                    result.append(line6)

        return result, totales

    def generate_records7(self, record_ids):
        result = []
        totales = []
        date_from = record_ids.date_from
        date_to = record_ids.date_to
        start_datetime = datetime.combine(date_from, time.min)  # 00:00:00
        end_datetime = datetime.combine(date_to, time.max).replace(microsecond=0)  # 23:59:59
        date_from_str = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
        date_to_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        company_id = record_ids.company_id
        moves = self.env['account.move'].search([('move_type', 'in', ['out_invoice']),
                                                 ('state', '=', 'posted'),
                                                 ('date_certification', '>=', date_from_str),
                                                 ('date_certification', '<=', date_to_str),
                                                 ('company_id', '=', company_id.id)], order='date,name')

        company_partner = company_id.partner_id
        if moves and company_partner.type_consumer_taxp == 'taxpayer' and company_partner.taxpayer_type == 'medium':
            for move in moves:
                swich = False
                nit, dui = self.get_nit_dui(move.partner_id)
                tipo_doc = self.get_type_document(move.fe_type)
                monto_sujeto = 0.0
                retencion_1 = 0.0
                for l in move.invoice_line_ids:
                    if l.tax_ids:
                        taxes = l.tax_ids.compute_all(l.price_unit, company_id.currency_id, l.quantity, l.product_id, move.partner_id)
                        for tax in taxes['taxes']:
                            imp = self.env['account.tax'].browse(tax['id'])
                            if 'gran contribuyente' in imp.name.lower():
                                monto_sujeto += l.price_subtotal
                                retencion_1 += tax['amount']
                                swich = True
                if swich == True:
                    line7 = {
                        'nit': nit,
                        'fecha_emision': self.char_to_date(move.date_certification) if move.date_certification else False,
                        'tipo_doc': tipo_doc,
                        'serie': move.number_of_series_document if move.number_of_series_document else 0,
                        'numero_doc': move.uuid_code.replace("-", "") if move.uuid_code else '',
                        'monto_sujeto': monto_sujeto,
                        'retencion_1': retencion_1,
                        'dui': dui,
                        'anex': move.number_of_annexed_7 if move.number_of_annexed_7 else 0,

                    }
                    result.append(line7)

        return result, totales

    def generate_records8(self, record_ids):
        result = []
        totales = []
        date_from = record_ids.date_from
        date_to = record_ids.date_to
        start_datetime = datetime.combine(date_from, time.min)  # 00:00:00
        end_datetime = datetime.combine(date_to, time.max).replace(microsecond=0)  # 23:59:59
        date_from_str = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
        date_to_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        company_id = record_ids.company_id
        moves = self.env['account.move'].search([('move_type', 'in', ['in_invoice']),
                                                 ('state', '=', 'posted'),
                                                 ('date_certification', '>=', date_from_str),
                                                 ('date_certification', '<=', date_to_str),
                                                 ('company_id', '=', company_id.id)], order='date,name')

        company_partner = company_id.partner_id
        if moves and company_partner.type_consumer_taxp == 'taxpayer' and company_partner.taxpayer_type == 'medium':
            for move in moves:
                swich = False
                nit, dui = self.get_nit_dui(move.partner_id)
                fe_type = move.fe_type
                tipo_doc = self.get_type_document(fe_type)
                monto_sujeto = 0.0
                percepcion_1 = 0.0
                for l in move.invoice_line_ids:
                    if l.tax_ids:
                        taxes = l.tax_ids.compute_all(l.price_unit, company_id.currency_id, l.quantity, l.product_id, move.partner_id)
                        for tax in taxes['taxes']:
                            imp = self.env['account.tax'].browse(tax['id'])
                            if 'percepción de iva' in imp.name.lower():
                                if monto_sujeto == 0.0:
                                    monto_sujeto += l.price_subtotal
                                percepcion_1 += tax['amount']
                                swich = True
                            elif 'iva por cobrar' in imp.name.lower():
                                # swich = True
                                if monto_sujeto == 0.0:
                                    monto_sujeto += l.price_subtotal
                if swich == True:
                    line8 = {
                        'nit_agente': nit,
                        'fecha_emision': self.char_to_date(move.date_certification) if move.date_certification else False,
                        'tipo_doc': fe_type if fe_type else '',
                        'serie': move.number_of_series_document_supplier if move.number_of_series_document_supplier else '',
                        'numero_doc': move.uuid_user if move.uuid_user else '',
                        'monto_sujeto': monto_sujeto,
                        'percepcion_1': percepcion_1,
                        'dui_agente': dui,
                        'anex': move.number_of_annexed_8 if move.number_of_annexed_8 else 0,

                    }
                    result.append(line8)

        return result, totales

    def generate_records9(self, record_ids):
        result = []
        totales = []
        date_from = record_ids.date_from
        date_to = record_ids.date_to
        start_datetime = datetime.combine(date_from, time.min)  # 00:00:00
        end_datetime = datetime.combine(date_to, time.max).replace(microsecond=0)  # 23:59:59
        date_from_str = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
        date_to_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        company_id = record_ids.company_id
        moves = self.env['account.move'].search([('move_type', 'in', ['in_invoice']),
                                                 ('state', '=', 'posted'),
                                                 ('date_certification', '>=', date_from_str),
                                                 ('date_certification', '<=', date_to_str),
                                                 ('company_id', '=', company_id.id)], order='date,name')

        company_partner = company_id.partner_id
        if moves and company_partner.type_consumer_taxp == 'taxpayer' and company_partner.taxpayer_type == 'big':
            for move in moves:
                impuesto = False
                nit, dui = self.get_nit_dui(move.partner_id)
                tipo_doc = self.get_type_document(move.fe_type)
                monto_sujeto = 0.0
                percepcion_1 = 0.0
                for l in move.invoice_line_ids:
                    if l.tax_ids:
                        taxes = l.tax_ids.compute_all(l.price_unit, company_id.currency_id, l.quantity, l.product_id, move.partner_id)
                        for tax in taxes['taxes']:
                            imp = self.env['account.tax'].browse(tax['id'])
                            if 'percepción de iva' in imp.name.lower():
                                monto_sujeto += l.price_subtotal
                                percepcion_1 += tax['amount']
                                impuesto = True
                if impuesto == True:
                    line9 = {
                        'nit_sujeto': nit,
                        'fecha_emision': self.char_to_date(move.date_certification) if move.date_certification else False,
                        'tipo_doc': tipo_doc,
                        'resolucion': move.number_resolution if move.number_resolution else '',
                        'serie': move.number_of_series_document_supplier if move.number_of_series_document_supplier else '',
                        'numero_documento': move.uuid_user if move.uuid_user else '',
                        'monto_sujeto': monto_sujeto,
                        'percepcion_1': percepcion_1,
                        'dui_sujeto': dui,
                        'anex': move.number_of_annexed_9 if move.number_of_annexed_9 else 0,

                    }
                    result.append(line9)
        return result, totales

    def generate_records10(self, record_ids):
        result = []
        totales = []
        date_from = record_ids.date_from
        date_to = record_ids.date_to
        start_datetime = datetime.combine(date_from, time.min)  # 00:00:00
        end_datetime = datetime.combine(date_to, time.max).replace(microsecond=0)  # 23:59:59
        date_from_str = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
        date_to_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        company_id = record_ids.company_id
        moves = self.env['account.move'].search([('move_type', 'in', ['out_invoice']),
                                                 ('state', '=', 'posted'),
                                                 ('date_certification', '>=', date_from_str),
                                                 ('date_certification', '<=', date_to_str),
                                                 ('company_id', '=', company_id.id)], order='date,name')

        company_partner = company_id.partner_id
        if moves and company_partner.type_consumer_taxp == 'taxpayer' and company_partner.taxpayer_type == 'big':
            for move in moves:
                impuesto = False
                nit, dui = self.get_nit_dui(move.partner_id)
                tipo_doc = self.get_type_document(move.fe_type)
                monto_sujeto = 0.0
                retencion_1 = 0.0
                for l in move.invoice_line_ids:
                    if l.tax_ids:
                        taxes = l.tax_ids.compute_all(l.price_unit, company_id.currency_id, l.quantity, l.product_id, move.partner_id)
                        for tax in taxes['taxes']:
                            imp = self.env['account.tax'].browse(tax['id'])
                            if 'retención de iva' in imp.name.lower():
                                monto_sujeto += l.price_subtotal
                                retencion_1 += tax['amount']
                                impuesto = True
                if impuesto == True:
                    line10 = {
                        'nit_sujeto': nit,
                        'fecha_emision': self.char_to_date(move.date_certification) if move.date_certification else False,
                        'tipo_doc': tipo_doc,
                        'resolucion': move.number_of_resolution if move.number_of_resolution else '',
                        'serie': move.number_of_series_document if move.number_of_series_document else 0,
                        'numero_documento': move.uuid_code.replace("-", "") if move.uuid_code else '',
                        'monto_sujeto': monto_sujeto,
                        'retencion_1': retencion_1,
                        'dui_sujeto': dui,
                        'anex': move.number_of_annexed_10 if move.number_of_annexed_10 else 0,
                    }
                    result.append(line10)

        return result, totales

    def generate_records11(self, record_ids):
        result = []
        totales = []
        date_from = record_ids.date_from
        date_to = record_ids.date_to
        start_datetime = datetime.combine(date_from, time.min)  # 00:00:00
        end_datetime = datetime.combine(date_to, time.max).replace(microsecond=0)  # 23:59:59
        date_from_str = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
        date_to_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        company_id = record_ids.company_id
        moves = self.env['account.move'].search([('move_type', 'in', ['in_invoice']),
                                                 ('state', '=', 'posted'),
                                                 ('date_certification', '>=', date_from_str),
                                                 ('date_certification', '<=', date_to_str),
                                                 ('company_id', '=', company_id.id)], order='date,name')

        company_partner = company_id.partner_id
        if moves and company_partner.type_consumer_taxp == 'taxpayer' and company_partner.taxpayer_type == 'big':
            for move in moves:
                impuesto = False
                nit, dui = self.get_nit_dui(move.partner_id)
                monto_sujeto = 0.0
                anticipo_2 = 0.0
                for l in move.invoice_line_ids:
                    if l.tax_ids:
                        taxes = l.tax_ids.compute_all(l.price_unit, company_id.currency_id, l.quantity, l.product_id, move.partner_id)
                        for tax in taxes['taxes']:
                            imp = self.env['account.tax'].browse(tax['id'])
                            if 'anticipo a cuenta' in imp.name.lower():
                                monto_sujeto += l.price_subtotal
                                anticipo_2 += tax['amount']
                                impuesto = True
                if impuesto == True:
                    line11 = {
                        'nit_sujeto': nit,
                        'fecha_emision': self.char_to_date(move.date_certification) if move.date_certification else False,
                        'resolucion': move.number_resolution if move.number_resolution else '',
                        'serie': move.number_of_series_document_supplier if move.number_of_series_document_supplier else '',
                        'numero_doc': move.uuid_user if move.uuid_user else '',
                        'monto_sujeto': monto_sujeto,
                        'anticipo_2': anticipo_2,
                        'dui_sujeto': dui,
                        'anex': move.number_of_annexed_11 if move.number_of_annexed_11 else 0,
                    }
                    result.append(line11)


        return result, totales

    def generate_records12(self, record_ids):
        result = []
        totales = []
        # date_from = record_ids.date_from
        # date_to = record_ids.date_to
        # company_id = record_ids.company_id
        # moves = self.env['account.move'].search([('move_type', 'in', ['out_invoice']),
        #                                          ('state', '=', 'posted'),
        #                                          ('invoice_date', '>=', date_from),
        #                                          ('invoice_date', '<=', date_to),
        #                                          ('company_id', '=', company_id.id)], order='date,name')
        #
        # if moves:
        #     for move in moves.filtered(lambda l: l.partner_id.type_consumer_taxp == 'consumer'):
        #         nit, dui = self.get_nit_dui(move.partner_id)
        #         tipo_doc = self.get_type_document(move.fe_type)
        #         monto_sujeto = 0.0
        #         retencion_13 = 0.0
        #         for l in move.invoice_line_ids:
        #             if l.tax_ids:
        #                 taxes = l.tax_ids.compute_all(l.price_unit, company_id.currency_id, l.quantity, l.product_id, move.partner_id)
        #                 for tax in taxes['taxes']:
        #                     imp = self.env['account.tax'].browse(tax['id'])
        #                     if 'iva por pagar consumidores finales' in imp.name.lower():
        #                         monto_sujeto += l.price_subtotal
        #                         retencion_13 += tax['amount']
        #         line12 = {
        #             'nit_sujeto': nit,
        #             'fecha_emision': move.invoice_date if move.invoice_date else False,
        #             'tipo_doc': tipo_doc,
        #             'serie': move.number_of_series_document if move.number_of_series_document else 0,
        #             'resolution': move.number_of_resolution if move.number_of_resolution else '',
        #             'numero_documento': move.uuid_code.replace("-", "") if move.uuid_code else '',
        #             'monto_sujeto': monto_sujeto,
        #             'retencion_13': retencion_13,
        #             'dui_sujeto': dui,
        #             'anex': move.number_of_annexed_12 if move.number_of_annexed_12 else 0,
        #
        #         }
        #         result.append(line12)
        return result, totales

    def get_min_max_uuid_code(self, result, dict_uuid_code):
        if result:
            for key, value in dict_uuid_code.items():
                if value:
                    value.sort(key=lambda x: x[0])

            for line in result:
                fecha = line.get('fecha', False)
                if fecha:
                    uuid_code_list = dict_uuid_code.get(fecha)
                    if uuid_code_list:
                        value = {
                            'numero_documento_del': uuid_code_list[0][1],
                            'numero_documento_al': uuid_code_list[-1][1],
                        }
                        line.update(value)

    def get_type_document(self, type):
        fe_type = ''
        if type:
            if type == '01':
                fe_type = 'Factura'
            elif type == '03':
                fe_type = 'Comprobante de Crédito Fiscal'
            elif type == '04':
                fe_type = 'Nota de Remisión'
            elif type == '05':
                fe_type = 'Nota de Crédito'
            elif type == '06':
                fe_type = 'Nota de Débito'
            elif type == '11':
                fe_type = 'Facturas de Exportación'
            else:
                fe_type = 'Factura de Sujeto Excluido'
        return fe_type

    def get_nrc(self, move):
        if move.partner_id.nrc:
            if move.partner_id.identification_type == '13':
                if move.partner_id.dui_field:
                    nrc = ''
                else:
                    nrc = move.partner_id.nrc
            else:
                nrc = move.partner_id.nrc
        else:
            nrc = ''
        return nrc

    def get_number_name_document(self, partner):
        if partner.identification_type == '36':
            name = '1'
            # name = 'NIT'
            name_document = partner.vat
            return name, name_document
        elif partner.identification_type == '13':
            name = '2'
            # name = 'DUI'
            name_document = partner.dui_field
            return name, name_document
        elif partner.identification_type == '37':
            name = '3'
            # name = 'Otro'
            name_document = partner.other_field
            return name, name_document
        elif partner.identification_type == '03':
            name = '3'
            # name = 'Pasaporte'
            name_document = partner.passport_field
            return name, name_document
        elif partner.identification_type == '02':
            name = '3'
            # name = 'Carnet de Residente'
            name_document = partner.carnet_residente_field
            return name, name_document
        else:
            name = ''
            name_document = False
            return name, name_document

    def get_document_classification(self, document_classification):
        if document_classification == '1':
            return '[1]Costo'
        elif document_classification == '2':
            return '[2]Gasto'
        else:
            return ''

    def get_type_of_operation(self, type_of_operation):
        if type_of_operation == '1':
            return '[1]Gravada'
        elif type_of_operation == '2':
            return '[2]No Gravada'
        elif type_of_operation == '3':
            return '[3]Excluido o no constituye renta'
        else:
            return ''

    def get_sector(self, sector):
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

    def get_type_of_cost_or_expense(self, type_of_cost_or_expense):
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


    def get_nit_dui(self, partner):
        if partner.identification_type == '13':
            if partner.dui_field:
                return '', partner.dui_field
            else:
                return '', ''
        else:
            if partner.identification_type == '36':
                if partner.vat:
                    return partner.vat, ''
                else:
                    return '', ''
            else:
                return '', ''



    def get_dui_nrc(self, move):
        if move.partner_id.identification_type == '13':
            if move.partner_id.dui_field:
                return move.partner_id.dui_field, ''
            else:
                return '', ''
        else:
            if move.partner_id.nrc:
                return '', move.partner_id.nrc
            else:
                return '', ''

    def insert_dash_before_last_nrc(self, nrc):
        if len(nrc) > 1:
            return nrc[:-1] + '-' + nrc[-1]
        return nrc

    def char_to_date(self, fecha_str):
        return datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S").date()






