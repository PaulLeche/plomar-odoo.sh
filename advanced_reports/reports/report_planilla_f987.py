# -*- encoding: utf-8 -*-

from odoo.tools.translate import _
from odoo import fields, models, api
import json
from dateutil.relativedelta import relativedelta
from odoo.tools import float_round
import time, datetime

class ReportPlanillaF987(models.AbstractModel):
    _name = 'report.advanced_reports.report_planilla_f987'
    _description = 'report advanced_reports report_planilla_f987'


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

    def _get_nit(self, partner_id):
        vat = ''
        if partner_id:
            if partner_id.vat:
                vat = partner_id.vat.replace("-", "")
        return vat

    def get_fe_type(self, move):
        fe_type = ''
        if move.fe_type:
            if move.fe_type == '01':
                fe_type = 'Factura'
            elif move.fe_type == '03':
                fe_type = 'Comprobante de Crédito Fiscal'
            elif move.fe_type == '04':
                fe_type = 'Nota de Remisión'
            elif move.fe_type == '05':
                fe_type = 'Nota de Crédito'
            elif move.fe_type == '06':
                fe_type = 'Nota de Débito'
            elif move.fe_type == '11':
                fe_type = 'Facturas de Exportación'
            elif move.fe_type == '14':
                fe_type = 'Factura de Sujeto Excluido'
        return fe_type

    def get_fe_generation(self, move):
        fe_generation = ''
        if move.fe_generation:
            if move.fe_generation == '01':
                fe_generation = 'Físico'
            elif move.fe_generation == '02':
                fe_generation = 'Electrónico'
        return fe_generation

    def get_concept_operation(self, move):
        concept_operation = ''
        if move.concept_operation:
            if move.concept_operation == 'import':
                concept_operation = '[1]Importación'
            elif move.concept_operation == 'internment':
                concept_operation = '[2]Internación'
            elif move.concept_operation == 'services':
                concept_operation = '[3]Importación de servicios'
        return concept_operation

    def get_identification_type(self, partner_id):
        identification_type = ''
        if partner_id and partner_id.identification_type:
            if partner_id.identification_type == '36':
                identification_type = 'NIT'
            elif partner_id.identification_type == '13':
                identification_type = 'DUI'
            elif partner_id.identification_type == '37':
                identification_type = 'Otro'
            elif partner_id.identification_type == '03':
                identification_type = 'Pasaporte'
            elif partner_id.identification_type == '02':
                identification_type = 'Carnet de residente'
        return identification_type
    def get_identification(self, partner_id):
        identification = ''
        if partner_id and partner_id.identification_type:
            if partner_id.identification_type == '36' and partner_id.vat:
                identification = partner_id.vat
            elif partner_id.identification_type == '13' and partner_id.dui_field:
                identification = partner_id.dui_field
            elif partner_id.identification_type == '37' and partner_id.other_field:
                identification = partner_id.other_field
            elif partner_id.identification_type == '03' and partner_id.passport_field:
                identification = partner_id.passport_field
            elif partner_id.identification_type == '02' and partner_id.carnet_residente_field:
                identification = partner_id.carnet_residente_field
        return identification

    def get_representante(self, partner_id):
        representante = partner_id.name
        if partner_id and partner_id.tipo_persona:
            if partner_id.tipo_persona == '1':
                representante = 'No aplica'
            elif partner_id.tipo_persona == '2' and partner_id.child_ids:
                name = ''
                for child in partner_id.child_ids:
                    if child.name:
                        if name == '':
                            name = name + child.name
                        else:
                            name = name + ', ' + child.name
                representante = name
        return representante

    def get_country(self, partner_id):
        country = ''
        if partner_id and partner_id.country_id:
            if partner_id.country_id.code:
                country = partner_id.country_id.code
        return country

    def get_import_type(self, move):
        import_type = ''
        if move and move.import_type:
            if move.import_type == 'statement':
                import_type = '[1]Declaración de Mercancía'
            elif move.import_type == 'form':
                import_type = '[2]Formulario Aduanero'
            elif move.import_type == 'fyduca':
                import_type = '[3]FYDUCA'
            elif move.import_type == 'other':
                import_type = '[4]Otro'
        return import_type

    def get_departament(self, partner_id):
        departament = ''
        if partner_id and partner_id.fe_address_dep:
           if partner_id.fe_address_dep.name_depart:
               departament = partner_id.fe_address_dep.name_depart
        return departament

    def get_fe_address_mun(self, partner_id):
        fe_address_mun = ''
        if partner_id and partner_id.fe_address_mun:
            if partner_id.fe_address_mun.name_muni:
                fe_address_mun = partner_id.fe_address_mun.name_muni
        return fe_address_mun

    def get_rate(self, currency_id):
        rate_dollar = 1.0
        if currency_id and currency_id.rate_ids:
            latest_rate = currency_id.rate_ids.sorted(key=lambda r: r.name, reverse=True)
            if latest_rate :
                rate_dollar = latest_rate[0].inverse_company_rate
        return rate_dollar

    def generate_records_provinscrito (self, record_ids):
        result = []
        totales = []
        total_amount = 0.0
        total_iva = 0.0
        date_from = record_ids.date_from
        date_to = record_ids.date_to
        company_id = record_ids.company_id
        moves = self.env['account.move'].search([('move_type', 'in', ['in_invoice']),
                                                 ('state', '=', 'posted'),
                                                 ('invoice_date', '>=', date_from),
                                                 ('invoice_date', '<=', date_to),
                                                 ('fe_type', 'in', ['01', '03', '05', '06']),
                                                 ('company_id', '=', company_id.id)], order='date,name')

        if moves:
            for move in moves:
                vat = self._get_nit(move.partner_id)
                fe_type = self.get_fe_type(move)
                fe_generation = self.get_fe_generation(move)
                amount = 0.0
                iva = 0.0
                for l in move.invoice_line_ids:
                    if l.tax_ids:
                        amount_line = 0.0
                        taxes = l.tax_ids.compute_all(l.price_unit, company_id.currency_id, l.quantity, l.product_id, move.partner_id)
                        for tax in taxes['taxes']:
                            imp = self.env['account.tax'].browse(tax['id'])
                            if amount_line == 0.0:
                                amount_line += tax['base']
                            if 'iva por cobrar' in imp.name.lower():
                                iva += tax['amount']
                        amount += amount_line
                    else:
                        amount += l.price_subtotal

                line_vinscrito = {
                    'invoice_date': move.invoice_date,
                    'month': self._month_letters(move.invoice_date.month),
                    'year': move.invoice_date.year,
                    'vat': vat,
                    'partner_name': move.partner_id.name if move.partner_id.name else '',
                    'fe_type': fe_type,
                    'fe_generation' : fe_generation,
                    'serie': move.number_of_series_document if move.number_of_series_document else '',
                    'preimpreso': move.document_number if move.document_number else '',
                    'nro_control': '0',
                    'amount': amount,
                    'iva': iva,
                    'anexo': '1',
                }
                result.append(line_vinscrito)
                total_amount += amount
                total_iva += iva

        totales = {
            'total_amount': total_amount,
            'total_iva': total_iva,
        }

        return result, totales

    def generate_records_provextranjero(self, record_ids):
        result = []
        totales = []
        date_from = record_ids.date_from
        date_to = record_ids.date_to
        company_id = record_ids.company_id
        total_amount = 0.0
        total_iva = 0.0
        moves = self.env['account.move'].search([('move_type', 'in', ['in_invoice']),
                                                 ('state', '=', 'posted'),
                                                 ('invoice_date', '>=', date_from),
                                                 ('invoice_date', '<=', date_to),
                                                 ('fe_type', 'in', ['11']),
                                                 ('company_id', '=', company_id.id)], order='date,name')
        if moves:
            for move in moves:
                amount = 0.0
                iva = 0.0
                for l in move.invoice_line_ids:
                    if l.tax_ids:
                        amount_line = 0.0
                        taxes = l.tax_ids.compute_all(l.price_unit, company_id.currency_id, l.quantity, l.product_id, move.partner_id)
                        for tax in taxes['taxes']:
                            imp = self.env['account.tax'].browse(tax['id'])
                            if amount_line == 0.0:
                                amount_line += tax['base']
                            iva += tax['amount']
                        amount += amount_line
                    else:
                        amount += l.price_subtotal

                line_provextranjero = {
                    'invoice_date': move.invoice_date,
                    'month': self._month_letters(move.invoice_date.month),
                    'year': move.invoice_date.year,
                    'concept_operation': self.get_concept_operation(move),
                    'identification_type' : self.get_identification_type(move.partner_id),
                    'nro_identification': self.get_identification(move.partner_id),
                    'partner_name': move.partner_id.name if move.partner_id.name else '',
                    'representante': self.get_representante(move.partner_id),
                    'country': self.get_country(move.partner_id),
                    'phone': move.partner_id.phone if move.partner_id.phone else '',
                    'doc_import': self.get_import_type(move),
                    'cod_aduana': move.aduana_code_id.name if move.aduana_code_id else '',
                    'num_doc': move.document_number if move.document_number else '',
                    'amount': amount,
                    'iva': iva,
                    'anexo': '2',

                }
                result.append(line_provextranjero)
                total_amount += amount
                total_iva += iva
        totales = {
            'total_amount': total_amount,
            'total_iva': total_iva,
        }

        return result, totales

    def generate_records_provexcluido(self, record_ids):
        result = []
        totales = []
        date_from = record_ids.date_from
        date_to = record_ids.date_to
        company_id = record_ids.company_id
        total_amount = 0.0
        moves = self.env['account.move'].search([('move_type', 'in', ['in_invoice']),
                                                ('state', '=', 'posted'),
                                                ('invoice_date', '>=', date_from),
                                                ('invoice_date', '<=', date_to),
                                                ('fe_type', 'in', ['14']),
                                                ('company_id', '=', company_id.id)], order='date,name')
        if moves:
            for move in moves:
                line_provexcluido = {
                    'invoice_date': move.invoice_date,
                    'month': self._month_letters(move.invoice_date.month),
                    'year': move.invoice_date.year,
                    'identification_type': self.get_identification_type(move.partner_id),
                    'nro_identification': self.get_identification(move.partner_id),
                    'partner_name': move.partner_id.name if move.partner_id.name else '',
                    'fe_type': self.get_fe_type(move),
                    'num_doc': move.document_number if move.document_number else '',
                    'phone': move.partner_id.phone if move.partner_id.phone else '',
                    'department': self.get_departament(move.partner_id),
                    'municipality': self.get_fe_address_mun(move.partner_id),
                    'complementary_address': move.partner_id.complement_address if move.partner_id.complement_address else '',
                    'street': move.partner_id.street if move.partner_id.street else '',
                    'house_number': move.partner_id.house_number if move.partner_id.house_number else '',
                    'local_apartment': move.partner_id.local_apartment if move.partner_id.local_apartment else '',
                    'address_information': move.partner_id.address_information if move.partner_id.address_information else '',
                    'email': move.partner_id.email if move.partner_id.email else '',
                    'amount': move.amount_total if move.amount_total else 0.0,
                    'anexo': '3',

                }
                result.append(line_provexcluido)
                total_amount += move.amount_total

        totales = {
            'total_amount': total_amount,
        }


        return result, totales

    def generate_records_cliente(self, record_ids):
        result = []
        totales = []
        date_from = record_ids.date_from
        date_to = record_ids.date_to
        company_id = record_ids.company_id
        moves = self.env['account.move'].search([('move_type', 'in', ['out_invoice']),
                                                 ('state', '=', 'posted'),
                                                 ('invoice_date', '>=', date_from),
                                                 ('invoice_date', '<=', date_to),
                                                 ('company_id', '=', company_id.id)], order='date,name')
        if moves:
            for move in moves:
                amount_total_dollar = 0.0
                currency_dollar_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
                rate_dollar = self.get_rate(currency_dollar_id)
                if move.currency_id.name == 'USD':
                    amount_total_dollar = move.amount_total
                else:
                    amount_total_dollar = (move.amount_total) * rate_dollar
                amount = 0.0
                iva = 0.0
                for l in move.invoice_line_ids:
                    if l.tax_ids:
                        amount_line = 0.0
                        taxes = l.tax_ids.compute_all(l.price_unit, company_id.currency_id, l.quantity, l.product_id, move.partner_id)
                        for tax in taxes['taxes']:
                            imp = self.env['account.tax'].browse(tax['id'])
                            if amount_line == 0.0:
                                amount_line += tax['base']
                            # if 'iva por cobrar' in imp.name.lower():
                            iva += tax['amount']
                        amount += amount_line
                    else:
                        amount += l.price_subtotal
                if move.fe_type == '01':
                    if amount_total_dollar >= 200:
                        line_cliente = {
                            'identification_type': self.get_identification_type(move.partner_id),
                            'nro_identification': self.get_identification(move.partner_id),
                            'partner_name': move.partner_id.name if move.partner_id.name else '',
                            'fe_type': self.get_fe_type(move),
                            'nro_control': move.numero_control if move.numero_control else '',
                            'invoice_date': move.invoice_date,
                            'month': self._month_letters(move.invoice_date.month),
                            'year': move.invoice_date.year,
                            'amount': amount,
                            'iva': iva,
                            'anexo': '4',

                        }
                        result.append(line_cliente)
                else:
                    line_cliente = {
                        'identification_type': self.get_identification_type(move.partner_id),
                        'nro_identification': self.get_identification(move.partner_id),
                        'partner_name': move.partner_id.name if move.partner_id.name else '',
                        'fe_type': self.get_fe_type(move),
                        'nro_control': move.numero_control if move.numero_control else '',
                        'invoice_date': move.invoice_date,
                        'month': self._month_letters(move.invoice_date.month),
                        'year': move.invoice_date.year,
                        'amount': amount,
                        'iva': iva,
                        'anexo': '4',

                    }
                    result.append(line_cliente)

        return result, totales

    def generate_records_cliente200(self, record_ids):
        result = []
        totales = []
        date_from = record_ids.date_from
        date_to = record_ids.date_to
        company_id = record_ids.company_id

        moves = self.env['account.move'].search([('move_type', 'in', ['out_invoice']),
                                                 ('state', '=', 'posted'),
                                                 ('invoice_date', '>=', date_from),
                                                 ('invoice_date', '<=', date_to),
                                                 ('fe_type', 'in', ['01']),
                                                 ('company_id', '=', company_id.id)], order='date,name')
        if moves:
            for move in moves:
                amount_total_dollar = 0.0
                currency_dollar_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
                rate_dollar = self.get_rate(currency_dollar_id)
                if move.currency_id.name == 'USD':
                    amount_total_dollar = move.amount_total
                else:
                    amount_total_dollar = (move.amount_total) * rate_dollar
                if amount_total_dollar <= 200:
                    amount = 0.0
                    iva = 0.0
                    for l in move.invoice_line_ids:
                        if l.tax_ids:
                            amount_line = 0.0
                            taxes = l.tax_ids.compute_all(l.price_unit, company_id.currency_id, l.quantity, l.product_id, move.partner_id)
                            for tax in taxes['taxes']:
                                imp = self.env['account.tax'].browse(tax['id'])
                                if amount_line == 0.0:
                                    if l.currency_id.name == 'USD':
                                        amount_line += tax['base']
                                    else:
                                        amount_line += (tax['base']) * rate_dollar
                                # if 'iva por cobrar' in imp.name.lower():
                                if l.currency_id.name == 'USD':
                                    iva += tax['amount']
                                else:
                                    iva += (tax['amount']) * rate_dollar
                            amount += amount_line
                        else:
                            amount += l.price_subtotal

                    line_cliente200 = {
                        'partner_name': move.partner_id.name if move.partner_id.name else '',
                        'invoice_date': move.invoice_date,
                        'month': self._month_letters(move.invoice_date.month),
                        'year': move.invoice_date.year,
                        'amount': amount,
                        'iva': iva,
                        'anexo': '5',
                    }
                    result.append(line_cliente200)
            result = sorted(result, key=lambda d: (d['partner_name'], d['invoice_date']))
            result = self.group_dictionary(result)
        return result, totales



    def group_dictionary(self, dictionary):
        partner_name1 = None
        invoice_date1 = None

        group = []
        quantity = 0
        amount = 0.0
        iva = 0.0
        for line in dictionary:
            partner_name2 = line.get('partner_name')
            invoice_date2 = line.get('invoice_date')
            if (partner_name2 != partner_name1 or invoice_date2 != invoice_date1) and partner_name1 and invoice_date1:
                line_group = {
                    'partner_name': partner_name1,
                    'invoice_date': invoice_date1,
                    'month': month,
                    'year': year,
                    'quantity': quantity,
                    'amount': amount,
                    'iva': iva,
                    'anexo': anexo,
                }
                group.append(line_group)
                quantity = 0
                amount = 0.0
                iva = 0.0

            partner_name1 = line.get('partner_name')
            invoice_date1 = line.get('invoice_date')
            month = line.get('month')
            year = line.get('year')
            quantity += 1
            amount += line.get('amount')
            iva += line.get('iva')
            anexo = line.get('anexo')

        if invoice_date1 or partner_name1:
            line_group = {
                'partner_name': partner_name1,
                'invoice_date': invoice_date1,
                'month': month,
                'year': year,
                'quantity': quantity,
                'amount': amount,
                'iva': iva,
                'anexo': anexo,
            }
            group.append(line_group)
        return group



