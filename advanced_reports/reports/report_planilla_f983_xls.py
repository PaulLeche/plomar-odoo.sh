# -*- encoding: utf-8 -*-

import time, datetime
import base64
import io
import logging

from odoo import fields, models, api
from datetime import datetime

_logger = logging.getLogger(__name__)


class ReportPlanillaF983Xls(models.AbstractModel):
    _name = 'report.advanced_reports.report_planilla_f983_xls'
    _description = 'report advanced_reports report_planilla_f983_xls'
    _inherit = ['report.report_xlsx.abstract']

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
        row = 2
        column = 1

        now = datetime.now()
        time_now = now.strftime("%Y/%m/%d %H:%M:%S")

        # SHEET AND STYLES
        sheet = workbook.add_worksheet("F983")


        title = workbook.add_format({'font_size': 20, 'bold': True, 'align': 'center', 'valign': 'vcenter'})
        title_no_border = workbook.add_format({'font_size': 16, 'bold': True, 'valign': 'vcenter', 'align': 'center'})
        date = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter'})
        bold = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter','border': 1, })
        no_bold = workbook.add_format({'font_size': 12, 'bold': False, 'valign': 'vcenter', 'border': 1, })
        no_bold_no_border = workbook.add_format({'font_size': 12, 'bold': False, 'valign': 'vcenter', 'align': 'center'})
        no_bold_no = workbook.add_format({'font_size': 12, 'bold': False, 'align': 'center', 'valign': 'vcenter', 'border': 1, })
        no_bold_paint = workbook.add_format({'bg_color': '#DCDCDC', 'font_size': 12, 'bold': False, 'align': 'center', 'valign': 'vcenter','border': 1, })
        no_bold_number = workbook.add_format({'font_size': 12, 'bold': False, 'align': 'right', 'valign': 'vcenter', 'border': 1, })
        no_bold_total = workbook.add_format({'font_size': 12, 'bold': False, 'align': 'right', 'valign': 'vcenter', 'border': 1, })
        total = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, })
        total_paint = workbook.add_format({'bg_color': '#DCDCDC', 'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter','border': 1, })
        total_right = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'right', 'valign': 'vcenter', 'border': 1, })


        # SET DINAMIC HEIGHT OF COLUMNS
        bold.set_text_wrap()
        no_bold_no.set_text_wrap()

        # GET VALUES
        # -------------------------Planilla ------------------------------------------
        result, ultima = self.env['report.advanced_reports.report_planilla_f983'].generate_records(record)

        # SIZE OF COLUMNS
        # WIDTH
        sheet.set_column('B:B', 50)
        sheet.set_column('C:C', 50)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 40)
        sheet.set_column('I:I', 40)
        sheet.set_column('J:J', 20)




        # HEIGTH
        sheet.set_row(1, 30)

        # SET MENU
        sheet.write('B2', 'DENOMINACIÓN DEL BIEN O DESCRIPCIÓN', bold)
        sheet.write('C2', 'CODIGO DE INVENTARIO DEL BIEN', bold)
        sheet.write('D2', 'UNIDAD DE MEDIDA', bold)
        sheet.write('E2', 'TOTAL DE UNIDADES/INVENTARIO FINAL', bold)
        sheet.write('F2', 'COSTO UNITARIO NETO SIN IVA ', bold)
        sheet.write('G2', 'COSTO TOTAL ', bold)
        sheet.write('H2', 'CATEGORÍA DEL BIEN', bold)
        sheet.write('I2', 'REFERENCIA EN LIBROS ', bold)
        sheet.write('J2', 'EJERCICIO FISCAL ', bold)


        if result:
            for line in result:
                sheet.write(row, column, line.get('product_name'), no_bold_no)
                sheet.write(row, column + 1, line.get('ref_internal'), no_bold_no)
                sheet.write(row, column + 2, line.get('uom_name'), no_bold_no)
                sheet.write(row, column + 3, '{0:,.2f}'.format(line.get('qty_available')), no_bold_no)
                sheet.write(row, column + 4, '{0:,.2f}'.format(line.get('standard_price')), no_bold_no)
                sheet.write(row, column + 5, '{0:,.2f}'.format(line.get('cost_total')), no_bold_no)
                sheet.write(row, column + 6, line.get('category_bien'), no_bold_no)
                sheet.write(row, column + 7, line.get('reference_books'), no_bold_no)
                sheet.write(row, column + 8, line.get('fiscal_exercise'), no_bold_no)

                row += 1




