# -*- encoding: utf-8 -*-

import time, datetime
import base64
import io
import logging

from odoo import fields, models, api
from datetime import datetime

_logger = logging.getLogger(__name__)


class ReportTaxpayerXls(models.AbstractModel):
    _name = 'report.advanced_reports.report_taxpayer_xls'
    _description = 'report advanced_reports report_taxpayer_xls'
    _inherit = ['report.report_xlsx.abstract']

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

    def generate_xlsx_report(self, workbook, data, balance):
        row = 7
        row2 = 8
        column = 1
        total_final = 0
        now = datetime.now()
        time_now = now.strftime("%Y/%m/%d %H:%M:%S")

        # SHEET AND STYLES
        sheet = workbook.add_worksheet("LIBRO DE VENTAS DE CONTRIBUYENTES")
        # sheet2 = workbook.add_worksheet("Cuenta por pagar")
        title = workbook.add_format({'font_size': 20, 'bold': True, 'align': 'center', 'valign': 'vcenter'})
        title_no_border = workbook.add_format({'font_size': 16, 'bold': True, 'valign': 'vcenter', 'align': 'center'})
        date = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter'})
        bold = workbook.add_format({'bg_color': '#D3D3D3', 'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter','border': 1, })
        no_bold = workbook.add_format({'font_size': 12, 'bold': False, 'valign': 'vcenter', 'border': 1, })
        no_bold_no_border = workbook.add_format({'font_size': 12, 'bold': False, 'valign': 'vcenter', 'align': 'center'})
        no_bold_no = workbook.add_format({'font_size': 12, 'bold': False, 'align': 'center', 'valign': 'vcenter', 'border': 1, })
        no_bold_paint = workbook.add_format({'bg_color': '#DCDCDC', 'font_size': 12, 'bold': False, 'align': 'center', 'valign': 'vcenter','border': 1, })
        no_bold_number = workbook.add_format({'font_size': 12, 'bold': False, 'align': 'right', 'valign': 'vcenter', 'border': 1, })
        no_bold_total = workbook.add_format({'font_size': 12, 'bold': False, 'align': 'right', 'valign': 'vcenter', 'border': 1, })
        total = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, })
        total_paint = workbook.add_format({'bg_color': '#DCDCDC', 'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter','border': 1, })
        total_right = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'right', 'valign': 'vcenter', 'border': 1, })

        # SET VALUES
        total_qty_he = 0
        total_otros_ingresos = 0
        company_name = balance[0].company_id.name if balance[0].company_id.name else ""
        company_street = balance[0].company_id.street if balance[0].company_id.street else ""
        company_street2 = balance[0].company_id.street2 if balance[0].company_id.street2 else ""
        company_city = balance[0].company_id.city if balance[0].company_id.city else ""
        company_zip = balance[0].company_id.zip if balance[0].company_id.zip else ""
        company_state_id = balance[0].company_id.state_id.name if balance[0].company_id.state_id else ""
        company_country_id = balance[0].company_id.country_id.name if balance[0].company_id.country_id else ""
        company_vat = balance[0].company_id.vat if balance[0].company_id.vat else ""
        company_nrc = balance[0].company_id.partner_id.nrc if balance[0].company_id.partner_id.nrc else ""

        # SET DINAMIC HEIGHT OF COLUMNS
        bold.set_text_wrap()
        no_bold_no.set_text_wrap()

        # GET VALUES
        result, ultima = self.env['report.advanced_reports.report_taxpayer'].generate_records(data)
        # -------------------------Libro de ventas a contribuyentes------------------------------------------
        # SIZE OF COLUMNS
        # WIDTH
        sheet.set_column('B:B', 8)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 40)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 60)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 20)
        sheet.set_column('I:I', 20)
        sheet.set_column('J:J', 20)
        sheet.set_column('K:K', 20)
        sheet.set_column('L:L', 20)
        sheet.set_column('M:M', 20)
        sheet.set_column('N:N', 20)
        sheet.set_column('O:O', 20)
        sheet.set_column('P:P', 20)
        sheet.set_column('Q:Q', 20)
        # HEIGTH
        # sheet.set_row(7, 25)

        # SET HEADER
        sheet.merge_range('B1:Q1', company_name, title_no_border)
        sheet.merge_range('B2:Q2', "LIBRO DE VENTAS DE CONTRIBUYENTES", title_no_border)
        sheet.merge_range('B3:Q3', "N.R.C. :" + company_nrc + " NIT : " + company_vat, no_bold_no_border)

        if ultima:
            sheet.merge_range('B4:Q4', "GIRO : " + ultima.get('giro'), no_bold_no_border)
        else:
            sheet.merge_range('B4:Q4', "GIRO : ", no_bold_no_border)

        sheet.merge_range('B5:Q5', 'Del ' + self._get_format_date(balance[0].date_from) + ' al ' + self._get_format_date(balance[0].date_to), no_bold_no_border)

        # # SET MENU
        sheet.merge_range('B6:B7', 'No', bold)
        sheet.merge_range('C6:C7', 'Fecha de Emisíon', bold)
        sheet.merge_range('D6:D7', 'No de Documento', bold)
        sheet.merge_range('E6:E7', 'N.R.C.', bold)
        sheet.merge_range('F6:F7', 'Nombre del cliente', bold)
        sheet.merge_range('G6:J6', 'Ventas propias', bold)
        sheet.write('G7', 'Exentas', bold)
        sheet.write('H7', 'No sujetas', bold)
        sheet.write('I7', 'Gravadas', bold)
        sheet.write('J7', 'Débito Fiscal', bold)
        sheet.merge_range('K6:M6', 'VENTAS A CUENTAS DE TERCEROS', bold)
        sheet.write('K7', 'Exentas', bold)
        sheet.write('L7', 'Gravadas', bold)
        sheet.write('M7', 'Débito Fiscal', bold)
        sheet.merge_range('N6:N7', 'IVA Retenido', bold)
        sheet.merge_range('O6:O7', 'Propina', bold)
        sheet.merge_range('P6:P7', 'Impuesto del Turismo', bold)
        sheet.merge_range('Q6:Q7', 'TOTAL VENTAS', bold)


        # # SET CURRENCY SYMBOL
        # currency = ultima.get('currency_gtq').symbol

        # SET LINES
        cont = 1
        if result:
            for line in result:
                sheet.write(row, column, cont, no_bold_no)
                sheet.write(row, column + 1, line.get('fecha_emision').strftime('%d/%m/%Y') if line.get('fecha_emision') else '', no_bold_no)
                sheet.write(row, column + 2, line.get('nro_doc'), no_bold_no)
                sheet.write(row, column + 3, line.get('nrc'), no_bold_no)
                sheet.write(row, column + 4, line.get('nombre_cliente'), no_bold_no)
                sheet.write(row, column + 5, '{0:,.2f}'.format(line.get('propias_exenta')), no_bold_no)
                sheet.write(row, column + 6, '{0:,.2f}'.format(line.get('propias_no_sujetas')), no_bold_no)
                sheet.write(row, column + 7, '{0:,.2f}'.format(line.get('propias_grabada')), no_bold_no)
                sheet.write(row, column + 8, '{0:,.2f}'.format(line.get('propias_debito')), no_bold_no)
                sheet.write(row, column + 9, '{0:,.2f}'.format(line.get('terceros_exenta')), no_bold_no)
                sheet.write(row, column + 10, '{0:,.2f}'.format(line.get('terceros_grabada')), no_bold_no)
                sheet.write(row, column + 11, '{0:,.2f}'.format(line.get('terceros_debito')), no_bold_no)
                sheet.write(row, column + 12, '{0:,.2f}'.format(line.get('iva_ret')), no_bold_no)
                sheet.write(row, column + 13, '{0:,.2f}'.format(line.get('propina')), no_bold_no)
                sheet.write(row, column + 14, '{0:,.2f}'.format(line.get('imp_turismo')), no_bold_no)
                sheet.write(row, column + 15, '{0:,.2f}'.format(line.get('total')),no_bold_no)

                row += 1
                cont +=1

                #         # SET TOTAL
            sheet.write(row, column + 5, '{0:,.2f}'.format(ultima.get('f_propias_exenta')), no_bold_no)
            sheet.write(row, column + 6, '{0:,.2f}'.format(ultima.get('f_propias_no_sujetas')), no_bold_no)
            sheet.write(row, column + 7, '{0:,.2f}'.format(ultima.get('f_propias_grabada')), no_bold_no)
            sheet.write(row, column + 8, '{0:,.2f}'.format(ultima.get('f_propias_debito')), no_bold_no)
            sheet.write(row, column + 9, '{0:,.2f}'.format(ultima.get('f_terceros_exenta')), no_bold_no)
            sheet.write(row, column + 10, '{0:,.2f}'.format(ultima.get('f_terceros_grabada')), no_bold_no)
            sheet.write(row, column + 11, '{0:,.2f}'.format(ultima.get('f_terceros_debito')), no_bold_no)
            sheet.write(row, column + 12, '{0:,.2f}'.format(ultima.get('f_iva_ret')), no_bold_no)
            sheet.write(row, column + 13, '{0:,.2f}'.format(ultima.get('f_propina')), no_bold_no)
            sheet.write(row, column + 14, '{0:,.2f}'.format(ultima.get('f_imp_turismo')), no_bold_no)
            sheet.write(row, column + 15, '{0:,.2f}'.format(ultima.get('f_total_ventas')), no_bold_no)
