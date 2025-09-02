# -*- encoding: utf-8 -*-

import time, datetime
import base64
import io
import logging

from odoo import fields, models, api
from datetime import datetime

_logger = logging.getLogger(__name__)


class ReportPlanillaF07Xls(models.AbstractModel):
    _name = 'report.advanced_reports.report_planilla_f14_xls'
    _description = 'report advanced_reports report_planilla_f14_xls'
    _inherit = ['report.report_xlsx.abstract']



    def generate_xlsx_report(self, workbook, data, record):
        row = 2
        column = 1
        total_final = 0
        now = datetime.now()
        time_now = now.strftime("%Y/%m/%d %H:%M:%S")

        # SHEET AND STYLES
        sheet = workbook.add_worksheet("Detalle")

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

        result, ultima = self.env['report.advanced_reports.report_planilla_f14'].generate_records(record)
        # ------------------------- Detalle ------------------------------------------
        # SIZE OF COLUMNS
        # WIDTH
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 60)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 40)
        sheet.set_column('I:I', 20)
        sheet.set_column('J:J', 20)
        sheet.set_column('K:K', 20)
        sheet.set_column('L:L', 20)
        sheet.set_column('M:M', 20)
        sheet.set_column('N:N', 20)
        sheet.set_column('O:O', 20)
        sheet.set_column('P:P', 20)
        sheet.set_column('Q:Q', 20)
        sheet.set_column('R:R', 20)
        sheet.set_column('S:S', 20)
        sheet.set_column('T:T', 60)
        sheet.set_column('U:U', 60)
        sheet.set_column('V:V', 60)
        sheet.set_column('W:W', 60)
        sheet.set_column('X:X', 20)


        # SET MENU
        sheet.write('B2', 'DOMICILIADO ', bold)
        sheet.write('C2', 'CÓDIGO DE PAÍS', bold)
        sheet.write('D2', 'APELLIDOS NOMBRES / RAZÓN SOCIAL (SOLO LETRAS MAYÚSCULAS)', bold)
        sheet.write('E2', 'NIT', bold)
        sheet.write('F2', 'DUI', bold)
        sheet.write('G2', 'Código de Ingreso', bold)
        sheet.write('H2', 'Monto Devengado (Para código de ingreso 01, 60 y 80: incluir AFP y Cotizaciones Sociales si aplican, No Incluir Aguinaldos, Bonificaciones y Gratificaciones)', bold)
        sheet.write('I2', 'Monto Devengado por Bonificaciones y Gratificaciones', bold)
        sheet.write('J2', 'Impuesto Retenido', bold)
        sheet.write('K2', 'Aguinaldo Exento', bold)
        sheet.write('L2', 'Aguinaldo Gravado', bold)
        sheet.write('M2', 'AFP', bold)
        sheet.write('N2', 'ISSS', bold)
        sheet.write('O2', 'INPEP', bold)
        sheet.write('P2', 'IPSFA', bold)
        sheet.write('Q2', 'CEFAFA', bold)
        sheet.write('R2', 'Bienestar Magisterial', bold)
        sheet.write('S2', 'ISSS IVM', bold)
        sheet.write('T2', 'Tipo de Operación (Renta)', bold)
        sheet.write('U2', 'Clasificación (Renta)', bold)
        sheet.write('V2', 'Sector (Renta)', bold)
        sheet.write('W2', 'Tipo de Costo / Gasto (Renta)', bold)
        sheet.write('X2', 'Periodo', bold)

        if result:
            for line in result:
                sheet.write(row, column, line.get('domiciled'), no_bold_no)
                sheet.write(row, column + 1, line.get('country_code'), no_bold_no)
                sheet.write(row, column + 2, line.get('name_partner'), no_bold_no)
                sheet.write(row, column + 3, line.get('nit'), no_bold_no)
                sheet.write(row, column + 4, line.get('dui'), no_bold_no)
                sheet.write(row, column + 5, line.get('entry_code'), no_bold_no)
                sheet.write(row, column + 6, '{0:,.2f}'.format(line.get('basic_salary')), no_bold_no)
                sheet.write(row, column + 7, '{0:,.2f}'.format(line.get('bonification_amount')), no_bold_no)
                sheet.write(row, column + 8, '{0:,.2f}'.format(line.get('tax_amount')), no_bold_no)
                sheet.write(row, column + 9, '{0:,.2f}'.format(line.get('exempt_bonus_amount')), no_bold_no)
                sheet.write(row, column + 10, '{0:,.2f}'.format(line.get('engraved_bonus_amount')), no_bold_no)
                sheet.write(row, column + 11, '{0:,.2f}'.format(line.get('afp_amount')), no_bold_no)
                sheet.write(row, column + 12, '{0:,.2f}'.format(line.get('isss_amount')), no_bold_no)
                sheet.write(row, column + 13, '{0:,.2f}'.format(line.get('inpep_amount')), no_bold_no)
                sheet.write(row, column + 14, '{0:,.2f}'.format(line.get('ipsfa_amount')), no_bold_no)
                sheet.write(row, column + 15, '{0:,.2f}'.format(line.get('cefafa_amount')), no_bold_no)
                sheet.write(row, column + 16, '{0:,.2f}'.format(line.get('teacher_welfare_amount')), no_bold_no)
                sheet.write(row, column + 17, '{0:,.2f}'.format(line.get('isss_ivm_amount')), no_bold_no)
                sheet.write(row, column + 18, line.get('type_of_operation'), no_bold_no)
                sheet.write(row, column + 19, line.get('classification'), no_bold_no)
                sheet.write(row, column + 20, line.get('sector'), no_bold_no)
                sheet.write(row, column + 21, line.get('type_cost'), no_bold_no)
                sheet.write(row, column + 22, line.get('period'), no_bold_no)

                row += 1



