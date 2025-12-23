# -*- encoding: utf-8 -*-

import time, datetime
import base64
import io
import logging

from odoo import fields, models, api
from datetime import datetime

_logger = logging.getLogger(__name__)


class ReportConsumerXls(models.AbstractModel):
    _name = 'report.advanced_reports.report_consumer_xls'
    _description = 'report advanced_reports report_consumer_xls'
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
        sheet = workbook.add_worksheet("LIBRO DE VENTAS A CONSUMIDOR")
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
        company_name = balance[0].company_id.name if balance[0].company_id.name else ""

        # SET DINAMIC HEIGHT OF COLUMNS
        bold.set_text_wrap()
        no_bold_no.set_text_wrap()

        # GET VALUES
        result, ultima = self.env['report.advanced_reports.report_consumer'].generate_records(data)
        # -------------------------Libro de ventas a contribuyentes------------------------------------------
        # SIZE OF COLUMNS
        # WIDTH
        sheet.set_column('B:B', 8)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 50)
        sheet.set_column('E:E', 70)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 20)
        sheet.set_column('I:I', 20)
        sheet.set_column('J:J', 20)
        sheet.set_column('K:K', 20)
        sheet.set_column('L:L', 20)
        sheet.set_column('M:M', 20)
        sheet.set_column('N:N', 20)
        sheet.set_column('O:O', 20)

        # HEIGTH
        sheet.set_row(7, 25)

        # SET HEADER
        sheet.merge_range('B1:O1', company_name, title_no_border)
        sheet.merge_range('B2:O2', "LIBRO DE VENTAS A CONSUMIDOR FINAL", title_no_border)
        sheet.merge_range('B3:O3', "N.R.C. :" + company_nrc + " NIT : " + company_vat, no_bold_no_border)

        if ultima:
            sheet.merge_range('B4:O4', "GIRO : " + ultima.get('giro'), no_bold_no_border)
        else:
            sheet.merge_range('B4:O4', "GIRO : ", no_bold_no_border)


        sheet.merge_range('B5:O5', 'Del ' + self._get_format_date(balance[0].date_from) + ' al ' + self._get_format_date(balance[0].date_to), no_bold_no_border)
        # # SET MENU
        sheet.merge_range('B6:B7', 'No', bold)
        sheet.merge_range('C6:C7', 'Fecha de Emisíon', bold)
        sheet.merge_range('D6:D7', 'No de Documento', bold)
        sheet.merge_range('E6:E7', 'Nombre del cliente', bold)
        sheet.merge_range('F6:I6', 'Ventas propias', bold)
        sheet.write('F7', 'Exentas', bold)
        sheet.write('G7', 'No sujetas', bold)
        sheet.write('H7', 'Locales', bold)
        sheet.write('I7', 'Exportacion', bold)
        sheet.merge_range('J6:J7', 'IVA 13%', bold)
        sheet.merge_range('K6:K7', 'Retención 1%', bold)
        sheet.merge_range('L6:L7', 'Cuenta de Terceros', bold)
        sheet.merge_range('M6:M7', 'Propina', bold)
        sheet.merge_range('N6:N7', 'Impuesto del Turismo', bold)
        sheet.merge_range('O6:O7', 'TOTAL VENTAS', bold)

        # SET LINES
        cont = 1
        if result:
            for line in result:
                sheet.write(row, column, cont, no_bold_no)
                sheet.write(row, column + 1, line.get('fecha_emision').strftime('%d/%m/%Y') if line.get('fecha_emision') else '', no_bold_no)
                sheet.write(row, column + 2, line.get('numero_documento'), no_bold_no)
                sheet.write(row, column + 3, line.get('nombre_cliente'), no_bold_no)
                sheet.write(row, column + 4, '{0:,.2f}'.format(line.get('propias_exenta')), no_bold_no)
                sheet.write(row, column + 5, '{0:,.2f}'.format(line.get('venta_no_sujeta')), no_bold_no)
                sheet.write(row, column + 6, '{0:,.2f}'.format(line.get('venta_local')), no_bold_no)
                sheet.write(row, column + 7, '{0:,.2f}'.format(line.get('venta_exportacion')), no_bold_no)
                sheet.write(row, column + 8, '{0:,.2f}'.format(line.get('iva_13')), no_bold_no)
                sheet.write(row, column + 9, '{0:,.2f}'.format(line.get('retencion_1')), no_bold_no)
                sheet.write(row, column + 10, '{0:,.2f}'.format(line.get('cuenta_terceros')), no_bold_no)
                sheet.write(row, column + 11, '{0:,.2f}'.format(line.get('propina')), no_bold_no)
                sheet.write(row, column + 12, '{0:,.2f}'.format(line.get('imp_turismo')), no_bold_no)
                sheet.write(row, column + 13, '{0:,.2f}'.format(line.get('total')),no_bold_no)

                row += 1
                cont += 1

                #         # SET TOTAL
            sheet.write(row, column + 4, '{0:,.2f}'.format(ultima.get('f_propias_exenta')), no_bold_no)
            sheet.write(row, column + 5, '{0:,.2f}'.format(ultima.get('f_venta_no_sujeta')), no_bold_no)
            sheet.write(row, column + 6, '{0:,.2f}'.format(ultima.get('f_venta_local')), no_bold_no)
            sheet.write(row, column + 7, '{0:,.2f}'.format(ultima.get('f_venta_exportacion')), no_bold_no)
            sheet.write(row, column + 8, '{0:,.2f}'.format(ultima.get('f_iva_13')), no_bold_no)
            sheet.write(row, column + 9, '{0:,.2f}'.format(ultima.get('f_retencion_1')), no_bold_no)
            sheet.write(row, column + 10, '{0:,.2f}'.format(ultima.get('total_terceros')),no_bold_no)
            sheet.write(row, column + 11, '{0:,.2f}'.format(ultima.get('f_propina')), no_bold_no)
            sheet.write(row, column + 12, '{0:,.2f}'.format(ultima.get('f_imp_turismo')), no_bold_no)
            sheet.write(row, column + 13, '{0:,.2f}'.format(ultima.get('f_total_ventas')), no_bold_no)
