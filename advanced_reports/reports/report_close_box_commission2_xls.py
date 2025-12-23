# -*- encoding: utf-8 -*-

import time, datetime
import base64
import io
import logging

from odoo import fields, models, api
from datetime import datetime

_logger = logging.getLogger(__name__)


class ReportCloseBoxXls(models.AbstractModel):
    _name = 'report.advanced_reports.report_close_box_commission_xls'
    _description = 'report advanced_reports report_close_box_commission_xls'
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
        no_bold_no2 = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, })
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
        result = self.env['report.advanced_reports.report_close_box_commission'].generate_records(record)
        if result:
            sheet = workbook.add_worksheet("Reporte cierre de caja para comisión")
            # WIDTH
            sheet.set_column('B:B', 50)
            sheet.set_column('C:C', 20)
            sheet.set_column('D:D', 20)
            sheet.set_column('E:E', 70)
            sheet.set_column('F:F', 40)
            sheet.set_column('G:G', 20)
            sheet.set_column('H:H', 70)
            sheet.set_column('I:I', 50)
            sheet.set_column('J:J', 20)
            sheet.set_column('K:K', 20)
            sheet.set_column('L:L', 20)
            sheet.set_column('M:M', 50)
            sheet.set_column('N:N', 30)

            # SET HEADER
            sheet.merge_range('B2:L2', record[0].company_id.name, title_no_border)
            sheet.merge_range('B3:L3', "REPORTE DE CIERRE DE CAJA PARA COMISIÒN", title_no_border)
            sheet.merge_range('B4:L4', 'Del ' + self._get_format_date(record[0].date_from) + ' al ' + self._get_format_date(record[0].date_to), no_bold_no_border)
            total_box = 0.0
            sum_total_box = 0.0
            column = 1
            column_final = 13
            row = 5
            sheet.write(row, column, 'Fecha factura', no_bold_no2)
            sheet.write(row, column + 1, 'Fecha cobro', no_bold_no2)
            sheet.write(row, column + 2, 'Dias de cobro', no_bold_no2)
            sheet.write(row, column + 3, 'Nombre cliente', no_bold_no2)
            sheet.write(row, column + 4, "Número DTE", no_bold_no2)
            sheet.write(row, column + 5, "Orden de venta", no_bold_no2)
            sheet.write(row, column + 6, "Nombre vendedor", no_bold_no2)
            sheet.write(row, column + 7, "Productos vendidos", no_bold_no2)
            sheet.write(row, column + 8, "Monto sin IVA", no_bold_no2)
            sheet.write(row, column + 9, "IVA", no_bold_no2)
            sheet.write(row, column + 10, "Total Factura", no_bold_no2)
            sheet.write(row, column + 11, "Total Cobro", no_bold_no2)
            sheet.write(row, column + 12, "Término de pago", no_bold_no2)

            row += 1

            for box, lines in result:
                if lines:
                    sheet.merge_range(row, column, row, column_final, box.upper(), no_bold_no1)
                    row += 1
                for line in lines:
                    sheet.write(row, column, line.get('invoice_invoice_date').strftime('%d/%m/%Y') if line.get('invoice_invoice_date') else '', no_bold_no)
                    sheet.write(row, column + 1, line.get('invoice_date').strftime('%d/%m/%Y') if line.get('invoice_date') else '', no_bold_no)

                    sheet.write(row, column + 2, line.get('payment_days'), no_bold_no)

                    sheet.write(row, column + 3, line.get('partner_name'), no_bold_no)
                    sheet.write(row, column + 4, line.get('numero_control'), no_bold_no)

                    sheet.write(row, column + 5, line.get('name_sale'), no_bold_no)

                    sheet.write(row, column + 6, line.get('saler_name'), no_bold_no)
                    sheet.write(row, column + 7, line.get('invoice_lines'), no_bold_no)
                    sheet.write(row, column + 8, line.get('amount_untaxed'), no_bold_no)
                    sheet.write(row, column + 9, line.get('amount_tax'), no_bold_no)
                    sheet.write(row, column + 10, '{0:,.2f}'.format(line.get('invoice_total')), no_bold_no)
                    sheet.write(row, column + 11, '{0:,.2f}'.format(line.get('amount_total')), no_bold_no)
                    sheet.write(row, column + 12, line.get('payment_term'), no_bold_no)
                    total_box += line.get('amount_total')
                    row += 1
                if lines:
                    sheet.merge_range(row, column, row, column_final - 1, 'TOTAL ' + box.upper(), no_bold_no2)
                    sheet.write(row, column_final, '{0:,.2f}'.format(total_box), no_bold_no)
                    sum_total_box += total_box
                    row += 1
            sheet.merge_range(row, column, row, column_final - 1, 'TOTAL', no_bold_no2)
            sheet.write(row, column_final, '{0:,.2f}'.format(sum_total_box), no_bold_no)