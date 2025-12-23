# -*- encoding: utf-8 -*-

import time, datetime
import base64
import io
import logging

from odoo import fields, models, api
from datetime import datetime

_logger = logging.getLogger(__name__)


class ReportPurchaseXls(models.AbstractModel):
    _name = 'report.advanced_reports.report_purchase_xls'
    _description = 'report advanced_reports report_purchase_xls'
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
        sheet = workbook.add_worksheet("LIBRO DE COMPRAS")
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
        result, ultima = self.env['report.advanced_reports.report_purchase'].generate_records(data)
        # -------------------------Libro de compras------------------------------------------
        # SIZE OF COLUMNS
        # WIDTH
        sheet.set_column('B:B', 8)
        sheet.set_column('C:C', 50)
        sheet.set_column('D:D', 20)
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
        sheet.set_row(7, 25)

        # SET HEADER
        sheet.merge_range('B2:P2', company_name, title_no_border)
        sheet.merge_range('B3:P3', "LIBRO DE COMPRAS", title_no_border)
        sheet.merge_range('B4:P4', "N.R.C. :" + company_nrc, title_no_border)
        sheet.merge_range('B5:P5', "NIT : " + company_vat, title_no_border)
        if ultima:
            sheet.merge_range('B6:P6', "GIRO : " + ultima.get('giro'), title_no_border)
        else:
            sheet.merge_range('B6:P6', "GIRO : ", title_no_border)
        # sheet.merge_range('B7:P7', "MES : " + self._month_letters(balance[0].date_to.month), no_bold_no_border)
        # sheet.merge_range('B8:P8', "AÑO : " + str(balance[0].date_to.year), no_bold_no_border)
        sheet.merge_range('B7:P7', 'Del ' + self._get_format_date(balance[0].date_from) + ' al ' + self._get_format_date(balance[0].date_to), no_bold_no_border)

        # IMAGE LOGO
        # if balance[0].company_id.logo:
        #     product_image = io.BytesIO(base64.b64decode(balance[0].company_id.logo))
        #     sheet.insert_image('B2', "image.png", {'image_data': product_image, 'x_scale': 0.25, 'y_scale': 0.18})
        # # SET MENU
        sheet.merge_range('B10:B11', 'No', bold)
        sheet.merge_range('C10:C11', 'DOCUMENTO', bold)
        sheet.merge_range('D10:D11', 'FECHA', bold)
        sheet.merge_range('E10:E11', 'No REGISTRO', bold)
        sheet.merge_range('F10:F11', 'PROVEEDOR', bold)
        sheet.merge_range('G10:J10', 'COMPRAS LOCALES', bold)
        sheet.write('G11', 'EXENTAS', bold)
        sheet.write('H11', 'NO SUJETAS', bold)
        sheet.write('I11', 'GRAVADAS', bold)
        sheet.write('J11', 'CRÉDITO FISCAL', bold)
        sheet.merge_range('K10:M10', 'IMPORTACIONES E INTERNACIONES', bold)
        sheet.write('K11', 'EXENTAS', bold)
        sheet.write('L11', 'GRAVADAS', bold)
        sheet.write('M11', 'POLIZA DE IMPORTACION', bold)
        sheet.merge_range('N10:N11', 'PERCEPCION 1%', bold)
        sheet.merge_range('O10:O11', 'ANTICIPO A CUENTA 2%', bold)
        sheet.merge_range('P10:P11', 'COMPRAS A SUJETOS EXCLUIDOS', bold)
        sheet.merge_range('Q10:Q11', 'TOTAL COMPRA', bold)


        # # SET CURRENCY SYMBOL
        # currency = ultima.get('currency_gtq').symbol

        # SET LINES
        cont = 1
        if result:
            for line in result:
                sheet.write(row + 4, column, cont, no_bold_no)
                sheet.write(row + 4, column + 1, line.get('numero_documento'), no_bold_no)
                sheet.write(row + 4, column + 2, line.get('fecha_emision').strftime('%d/%m/%Y') if line.get('fecha_emision') else '', no_bold_no)
                sheet.write(row + 4, column + 3, line.get('nro_registro'), no_bold_no)
                # sheet.write(row + 4, column + 4, line.get('nrc'), no_bold_no)
                sheet.write(row + 4, column + 4, line.get('nombre_cliente'), no_bold_no)
                sheet.write(row + 4, column + 5, '{0:,.2f}'.format(line.get('propias_exenta')), no_bold_no)
                sheet.write(row + 4, column + 6, '{0:,.2f}'.format(line.get('locales_propias')), no_bold_no)
                sheet.write(row + 4, column + 7, '{0:,.2f}'.format(line.get('propias_grabada')), no_bold_no)
                sheet.write(row + 4, column + 8, '{0:,.2f}'.format(line.get('credito_fiscal')), no_bold_no)
                sheet.write(row + 4, column + 9, '{0:,.2f}'.format(line.get('imp_exentas')), no_bold_no)
                sheet.write(row + 4, column + 10, '{0:,.2f}'.format(line.get('imp_grabadas')), no_bold_no)
                sheet.write(row + 4, column + 11, '{0:,.2f}'.format(line.get('imp_poliza')), no_bold_no)
                sheet.write(row + 4, column + 12, '{0:,.2f}'.format(line.get('percepcion_1')),no_bold_no)
                sheet.write(row + 4, column + 13, '{0:,.2f}'.format(line.get('anticipo_2')), no_bold_no)
                sheet.write(row + 4, column + 14, '{0:,.2f}'.format(line.get('sujetos_excluidos')),no_bold_no)
                sheet.write(row + 4, column + 15, '{0:,.2f}'.format(line.get('total_compras')), no_bold_no)

                row += 1
                cont += 1

                #         # SET TOTAL
            sheet.write(row + 4, column + 5, '{0:,.2f}'.format(ultima.get('f_propias_exenta')), no_bold_no)
            sheet.write(row + 4, column + 6, '{0:,.2f}'.format(ultima.get('f_locales_propias')), no_bold_no)
            sheet.write(row + 4, column + 7, '{0:,.2f}'.format(ultima.get('f_propias_grabada')), no_bold_no)
            sheet.write(row + 4, column + 8, '{0:,.2f}'.format(ultima.get('f_credito_fiscal')), no_bold_no)
            sheet.write(row + 4, column + 9, '{0:,.2f}'.format(ultima.get('f_imp_exentas')), no_bold_no)
            sheet.write(row + 4, column + 10, '{0:,.2f}'.format(ultima.get('f_imp_grabadas')), no_bold_no)
            sheet.write(row + 4, column + 11, '{0:,.2f}'.format(ultima.get('f_imp_poliza')), no_bold_no)
            sheet.write(row + 4, column + 12, '{0:,.2f}'.format(ultima.get('f_percepcion_1')), no_bold_no)
            sheet.write(row + 4, column + 13, '{0:,.2f}'.format(ultima.get('f_anticipo_2')), no_bold_no)
            sheet.write(row + 4, column + 14, '{0:,.2f}'.format(ultima.get('f_sujetos_excluidos')), no_bold_no)
            sheet.write(row + 4, column + 15, '{0:,.2f}'.format(ultima.get('f_total_compras')), no_bold_no)