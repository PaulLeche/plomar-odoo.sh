# -*- encoding: utf-8 -*-

import time, datetime
import base64
import io
import logging

from odoo import fields, models, api
from datetime import datetime

_logger = logging.getLogger(__name__)


class ReportCloseBoxXls(models.AbstractModel):
    _name = 'report.advanced_reports.report_close_box_xls'
    _description = 'report advanced_reports report_close_box_xls'
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


    def generate_xlsx_report(self, workbook, data, record):

        now = datetime.now()
        time_now = now.strftime("%Y/%m/%d %H:%M:%S")

        # SHEET AND STYLES
        # sheet = workbook.add_worksheet("Caja 1")
        title = workbook.add_format({'font_size': 20, 'bold': True, 'align': 'center', 'valign': 'vcenter'})
        title_no_border = workbook.add_format({'font_size': 16, 'bold': True, 'valign': 'vcenter', 'align': 'center'})
        date = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter'})
        bold = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter','border': 1, })
        no_bold = workbook.add_format({'font_size': 12, 'bold': False, 'valign': 'vcenter', 'border': 1, })
        no_bold_no_border = workbook.add_format({'font_size': 12, 'bold': False, 'valign': 'vcenter', 'align': 'center'})
        no_bold_no = workbook.add_format({'font_size': 12, 'bold': False, 'align': 'center', 'valign': 'vcenter', 'border': 1, })
        no_bold_no1 = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'left', 'valign': 'vcenter', 'border': 1, })
        no_bold_no_total = workbook.add_format({'font_size': 12, 'bold': False, 'align': 'center', 'valign': 'vcenter', 'border': 0, })
        no_bold_paint = workbook.add_format({'bg_color': '#DCDCDC', 'font_size': 12, 'bold': False, 'align': 'center', 'valign': 'vcenter','border': 1, })
        no_bold_number = workbook.add_format({'font_size': 12, 'bold': False, 'align': 'right', 'valign': 'vcenter', 'border': 1, })
        no_bold_total = workbook.add_format({'font_size': 12, 'bold': False, 'align': 'right', 'valign': 'vcenter', 'border': 1, })
        total = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, })
        total_paint = workbook.add_format({'bg_color': '#DCDCDC', 'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter','border': 1, })
        total_right = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'right', 'valign': 'vcenter', 'border': 1, })

        # SET VALUES
        total_qty_he = 0
        total_otros_ingresos = 0
        company_name = record[0].company_id.name if record[0].company_id.name else ""
        company_street = record[0].company_id.street if record[0].company_id.street else ""
        company_street2 = record[0].company_id.street2 if record[0].company_id.street2 else ""
        company_city = record[0].company_id.city if record[0].company_id.city else ""
        company_zip = record[0].company_id.zip if record[0].company_id.zip else ""
        company_state_id = record[0].company_id.state_id.name if record[0].company_id.state_id else ""
        company_country_id = record[0].company_id.country_id.name if record[0].company_id.country_id else ""
        company_vat = record[0].company_id.vat if record[0].company_id.vat else ""

        # SET DINAMIC HEIGHT OF COLUMNS
        bold.set_text_wrap()
        no_bold_no.set_text_wrap()

        # GET VALUES
        result = self.env['report.advanced_reports.report_close_box'].generate_records(record)
        if result:
            for box, chashier, lines in result:
                column = 1
                column_final = 4
                row = 6
                sheet = workbook.add_worksheet(box)
                payment_method1 = None
                amount_total1 = 0.0
                swich = True
                # WIDTH
                sheet.set_column('B:B', 50)
                sheet.set_column('C:C', 20)
                sheet.set_column('D:D', 50)
                sheet.set_column('E:E', 30)
                # SET HEADER
                sheet.merge_range('B2:E2', record[0].company_id.name, title_no_border)
                sheet.merge_range('B3:E3', "REPORTE DE CIERRE DE " + box.upper(), title_no_border)
                sheet.merge_range('B4:E4','Del ' + self._get_format_date(record[0].date_from) + ' al ' + self._get_format_date(record[0].date_to), no_bold_no_border)
                if lines:
                    sheet.merge_range('B5:E5', "Nombre del cajero: " + chashier, no_bold_no_border)
                else:
                    sheet.merge_range('B5:E5', "Nombre del cajero: ", no_bold_no_border)


                total_amount_box = 0.0
                for line in lines:
                    payment_method2 = line.get('payment_method')
                    amount_total2 = line.get('amount_total')
                    if payment_method2 != payment_method1:
                        if payment_method1 or payment_method1 == '':
                            sheet.merge_range(row, column, row, column_final - 1, 'TOTAL ' + payment_method1.upper(), no_bold_no)
                            sheet.write(row, column_final, '{0:,.2f}'.format(amount_total1), no_bold_no)
                            total_amount_box += amount_total1
                            amount_total1 = 0.0
                            row += 1
                            swich = True
                        payment_method1 = payment_method2
                    if swich == True:
                        sheet.merge_range(row, column, row, column_final, 'PAGOS CON : ' + line.get('payment_method').upper(), no_bold_no1)
                        swich = False
                        row += 1
                    sheet.write(row, column, line.get('partner_name'), no_bold_no)
                    sheet.write(row, column + 1, line.get('invoice_date').strftime('%d/%m/%Y') if line.get('invoice_date') else '', no_bold_no)
                    sheet.write(row, column + 2, line.get('numero_control'), no_bold_no)
                    sheet.write(row, column + 3, '{0:,.2f}'.format(line.get('amount_total')), no_bold_no)

                    row += 1
                    amount_total1 += amount_total2
                if payment_method1:
                    sheet.merge_range(row, column, row, column_final - 1, 'TOTAL ' + payment_method1.upper(), no_bold_no)
                    sheet.write(row, column_final, '{0:,.2f}'.format(amount_total1), no_bold_no)
                    total_amount_box += amount_total1

                sheet.write(row + 2, column_final - 1, 'TOTAL ' + box.upper(), no_bold_no_total)
                sheet.write(row + 2, column_final, '{0:,.2f}'.format(total_amount_box), no_bold_no_total)