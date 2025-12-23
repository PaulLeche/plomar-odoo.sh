# -*- encoding: utf-8 -*-

import time, datetime
import base64
import io
import logging

from odoo import fields, models, api
from datetime import datetime

_logger = logging.getLogger(__name__)


class ReportPlanillaF07Xls(models.AbstractModel):
    _name = 'report.advanced_reports.report_planilla_f930_xls'
    _description = 'report advanced_reports report_planilla_f930_xls'
    _inherit = ['report.report_xlsx.abstract']



    def generate_xlsx_report(self, workbook, data, record):
        row = 2
        column = 1
        total_final = 0
        now = datetime.now()
        time_now = now.strftime("%Y/%m/%d %H:%M:%S")

        # SHEET AND STYLES
        sheet = workbook.add_worksheet("F930")

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

        result, ultima = self.env['report.advanced_reports.report_planilla_f930'].generate_records(record)
        # ------------------------- Detalle ------------------------------------------
        # SIZE OF COLUMNS
        # WIDTH
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 50)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 50)
        sheet.set_column('I:I', 50)
        sheet.set_column('J:J', 20)
        sheet.set_column('K:K', 50)
        sheet.set_column('L:L', 20)

        # SET MENU
        sheet.merge_range('B2:B3', 'NIT', bold)
        sheet.merge_range('C2:C3', 'NOMBRE', bold)
        sheet.merge_range('D2:D3', 'CALIDAD EN LA QUE ACTUA ', bold)
        sheet.merge_range('E2:E3', 'MODALIDAD', bold)
        sheet.merge_range('F2:F3', 'CODIGO  DE  DOCUMENTO', bold)
        sheet.merge_range('G2:G3', 'FECHA DEL DOCUMENTO ', bold)
        sheet.merge_range('H2:H3', 'SERIE DE DOCUMENTO EMITIDO',bold)
        sheet.merge_range('I2:I3', 'NUMERO DEL DOCUMENTO', bold)
        sheet.merge_range('J2:J3', 'MONTO SUJETO', bold)
        sheet.merge_range('K2:K3', 'MONTO DE RETENCIÓN, PERCEPCIÓN, ANTICIPO A CUENTA DE IVA ', bold)
        sheet.merge_range('L2:L3', 'PERIODO A INFORMAR', bold)

        if result:
            for line in result:
                sheet.write(row, column, line.get('nit'), no_bold_no)
                sheet.write(row, column + 1, line.get('partner_name'), no_bold_no)
                sheet.write(row, column + 2, line.get('quality'), no_bold_no)
                sheet.write(row, column + 3, line.get('modality'), no_bold_no)
                sheet.write(row, column + 4, line.get('code_document'), no_bold_no)
                sheet.write(row, column + 5, line.get('date_move').strftime('%d/%m/%Y') if line.get('date_move') else '',no_bold_no)
                sheet.write(row, column + 6, line.get('serie_document'), no_bold_no)
                sheet.write(row, column + 7, line.get('number_document'), no_bold_no)
                sheet.write(row, column + 8, '{0:,.2f}'.format(line.get('subject_amount')), no_bold_no)
                sheet.write(row, column + 9, '{0:,.2f}'.format(line.get('ret_amount')), no_bold_no)
                sheet.write(row, column + 10, line.get('period'), no_bold_no)

                row += 1



