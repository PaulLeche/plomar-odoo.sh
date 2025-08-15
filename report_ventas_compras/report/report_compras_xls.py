# -*- encoding: utf-8 -*-

import time, datetime

from odoo import fields, models, api
from datetime import datetime, date
import base64
import io
import time

MONTHS = {
    'January': 'Enero', 
    'February': 'Febrero', 
    'March': 'Marzo', 
    'April': 'Abril', 
    'May': 'Mayo',
    'June': 'Junio', 
    'July': 'Julio', 
    'August': 'Agosto', 
    'September': 'Septiembre',
    'October': 'Octubre',
    'November': 'Noviembre', 
    'December': 'Diciembre'
}

class ReportPurchaseBookXlsx(models.AbstractModel):
    _name = 'report.report_ventas_compras.report_purchase_book_xls'
    _inherit = ['report.report_xlsx.abstract', 'report.report_ventas_compras.report_purchase_book']
    _description = "Report Purchase Book XLSX"

    def _get_format_date(self, date):
        B = MONTHS[ date.strftime('%B') ]
        return date.strftime('%d de '+ B + ' del %Y')

    def generate_xlsx_report(self, workbook, docids, data):
        report_name = "new"
        row = 9
        column = 1
        total_final = 0
        now = datetime.now()
        time_now = now.strftime("%Y/%m/%d %H:%M:%S")

        # SHEET AND STYLES 
        sheet = workbook.add_worksheet("Purchase Book")
        title = workbook.add_format({'font_size': 20, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        title_no_border = workbook.add_format({'font_size': 16, 'bold': True, 'valign': 'vcenter'})
        date = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        bold = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1,})
        no_bold = workbook.add_format({'font_size': 12, 'bold': False, 'valign': 'vcenter', 'border': 1,})
        no_bold_no_border = workbook.add_format({'font_size': 12, 'bold': False, 'valign': 'vcenter'})
        no_bold_no = workbook.add_format({'font_size': 12, 'bold': False, 'align': 'center', 'valign': 'vcenter', 'border': 1,})
        no_bold_number = workbook.add_format({'font_size': 12, 'bold': False, 'align': 'right', 'valign': 'vcenter', 'border': 1,})
        no_bold_total = workbook.add_format({'font_size': 12, 'bold': False, 'align': 'right', 'valign': 'vcenter', 'border': 1,})
        total = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'right', 'valign': 'vcenter', 'border': 1,})
        total_table = workbook.add_format({'font_size': 12, 'bold': True, 'valign': 'vcenter', 'border': 1,})
        total_table_center = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1,})
        total_amount_table = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'right', 'valign': 'vcenter', 'border': 1,})

        currency_number = workbook.add_format({'font_size': 12, 'bold': False, 'align': 'right', 'valign': 'vcenter', 'border': 1, 'num_format': 'Q #,##0.00'})
        currency_total = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'right', 'valign': 'vcenter', 'border': 1, 'num_format': 'Q #,##0.00'})
        currency_total_amount = workbook.add_format({'font_size': 12, 'bold': True, 'align': 'right', 'valign': 'vcenter', 'border': 1, 'num_format': 'Q #,##0.00'})


        # SET DINAMIC HEIGHT OF COLUMNS
        bold.set_text_wrap()

        # GET VALUES 
        lineas, ultima = self.generate_records(docids)
        if data.date_from == data.date_to:
            fecha = self._get_format_date(data.date_from)
        else:
            fecha = 'Del ' + self._get_format_date(data.date_from) + ' al ' + self._get_format_date(data.date_to)
        company_street = data.company_id.street if data.company_id.street else ""
        company_street2 = data.company_id.street2 if data.company_id.street2 else ""
        company_city = data.company_id.city if data.company_id.city else ""
        company_state_id = data.company_id.state_id.name if data.company_id.state_id else ""
        company_zip = data.company_id.zip if data.company_id.zip else ""
        company_country_id = data.company_id.country_id.name if data.company_id.country_id else ""
        company_vat = data.company_id.vat if data.company_id.vat else ""
        company_phone = data.company_id.phone if data.company_id.phone else ""

        # SIZE OF COLUMNS
        # WIDTH  
        sheet.set_column('B:B', 8)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 48)
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

        # HEIGTH 
        sheet.set_row(9, 20)
        sheet.set_row(10, 20)

        # SET HEADER 
        sheet.merge_range('E2:R2', data.company_id.name, title_no_border)
        sheet.merge_range('E3:R3', company_street + ", " + company_street2, no_bold_no_border)
        sheet.merge_range('E4:R4', company_city + " " + company_state_id + " " + company_zip + ", " + company_country_id, no_bold_no_border)
        sheet.merge_range('E5:R5', "NIT: " + company_vat, no_bold_no_border)
        sheet.merge_range('E6:R6', "Tel:" + company_phone, no_bold_no_border)
        
        sheet.merge_range('B8:R8', 'LIBRO DE COMPRAS', title)
        sheet.merge_range('B9:R9', fecha, date)
        
        # IMAGE LOGO 
        if data.company_id.logo:
            company_logo = io.BytesIO(base64.b64decode(data.company_id.logo))
            sheet.insert_image('B2', "image.png", {'image_data': company_logo, 'x_scale': 0.12, 'y_scale': 0.08})

        # SET MENU 
        sheet.merge_range('B10:B11', 'No.', bold)
        sheet.merge_range('C10:C11', 'Fecha de Emisión', bold)
        sheet.merge_range('D10:D11', 'Tipo', bold)
        sheet.merge_range('E10:E11', 'Serie', bold)
        sheet.merge_range('F10:F11', 'No. Documento', bold)
        sheet.merge_range('G10:G11', 'NIT', bold)
        sheet.merge_range('H10:H11', 'Nombre del Proveedor', bold)
        
        sheet.merge_range('I10:L10', 'Base Gravada', bold)
        sheet.write('I11', 'Bienes', bold)
        sheet.write('J11', 'Servicios', bold)
        sheet.write('K11', 'Importaciones', bold)
        sheet.write('L11', 'Combustible', bold)
        
        sheet.merge_range('M10:O10', 'Base Exenta', bold)
        sheet.write('M11:', 'Bienes', bold)
        sheet.write('N11', 'Servicios', bold)
        sheet.write('O11', 'Peq. C.', bold)
        
        sheet.merge_range('P10:P11', 'IVA', bold)
        sheet.merge_range('Q10:Q11', 'IDP', bold)
        sheet.merge_range('R10:R11', 'Total', bold)

        # SET LINES 
        for linea in lineas:  
            for line in linea[1]:
                sheet.write(row+2, column, line['no'], no_bold_no)
                sheet.write(row+2, column+1, line['fecha'], no_bold_no)
                sheet.write(row+2, column+2, line['tipo'], no_bold_no)
                sheet.write(row+2, column+3, line['serie'], no_bold_no)
                sheet.write(row+2, column+4, line['numero'], no_bold_no)
                sheet.write(row+2, column+5, line['nit_cliente'], no_bold_no)
                sheet.write(row+2, column+6, line['cliente'], no_bold)
                sheet.write(row+2, column+7, float(line['bienes_gravados']), currency_number)
                sheet.write(row+2, column+8, float(line['servicios_gravados']), currency_number)
                sheet.write(row+2, column+9, float(line['importacion_gravada']), currency_number)
                sheet.write(row+2, column+10, float(line['combustible_gravado']), currency_number)
                sheet.write(row+2, column+11, float(line['bienes_exento']), currency_number)
                sheet.write(row+2, column+12, float(line['servicios_exento']), currency_number)
                sheet.write(row+2, column+13, float(line['line_peq_contribuyente_exento']), currency_number)
                sheet.write(row+2, column+14, float(line['iva']), currency_number)
                sheet.write(row+2, column+15, float(line['idp']), currency_number)
                sheet.write(row+2, column+16, float(line['subtotal']), currency_number)

                row += 1

        # SET TOTALS
        linea_total = 'B'+str(row+3)+':H'+str(row+3)
        sheet.merge_range(linea_total, 'TOTALES', total)
        sheet.write(row+2, column+7, float(ultima['total_bienes_gravados']), currency_total)
        sheet.write(row+2, column+8, float(ultima['total_servicios_gravados']), currency_total)
        sheet.write(row+2, column+9, float(ultima['total_importacion_gravada']), currency_total)
        sheet.write(row+2, column+10, float(ultima['total_combustible_gravado']), currency_total)
        sheet.write(row+2, column+11, float(ultima['total_bienes_exento']), currency_total)
        sheet.write(row+2, column+12, float(ultima['total_servicios_exento']), currency_total)
        sheet.write(row+2, column+13, float(ultima['total_line_peq_contribuyente_exento']), currency_total)
        sheet.write(row+2, column+14, float(ultima['total_iva_final']), currency_total)
        sheet.write(row+2, column+15, float(ultima['total_idp_final']), currency_total)
        sheet.write(row+2, column+16, float(ultima['total_subtotal_final']), currency_total)
        
        # TABLE TOTALS
        sheet.merge_range('B'+str(row+6)+':E'+str(row+6), 'TOTALES POR FACTURAS', total_table_center)
        sheet.merge_range('B'+str(row+7)+':D'+str(row+7), 'TOTAL BIENES GRAVADOS', total_table)
        sheet.merge_range('B'+str(row+8)+':D'+str(row+8), 'TOTAL BIENES EXENTOS', total_table)
        sheet.merge_range('B'+str(row+9)+':D'+str(row+9), 'TOTAL SERVICIOS GRAVADOS', total_table)
        sheet.merge_range('B'+str(row+10)+':D'+str(row+10), 'TOTAL SERVICIOS EXENTOS', total_table)
        sheet.merge_range('B'+str(row+11)+':D'+str(row+11), 'TOTAL IMPORTACIÓN', total_table)
        sheet.merge_range('B'+str(row+12)+':D'+str(row+12), 'TOTAL PEQ. C.', total_table)
        sheet.merge_range('B'+str(row+13)+':D'+str(row+13), 'TOTAL COMBUSTIBLES', total_table)
        sheet.merge_range('B'+str(row+14)+':D'+str(row+14), 'TOTAL IVA', total_table)
        sheet.merge_range('B'+str(row+15)+':D'+str(row+15), 'TOTAL IDP', total_table)
        sheet.merge_range('B'+str(row+16)+':D'+str(row+16), 'TOTAL RETENCIONES', total_table)
        sheet.merge_range('B'+str(row+17)+':D'+str(row+17), '**TOTAL**', total_table)
        
        sheet.write('E'+str(row+7), float(ultima['total_bienes_gravados']), currency_total_amount)
        sheet.write('E'+str(row+8), float(ultima['total_bienes_exento']), currency_total_amount)
        sheet.write('E'+str(row+9), float(ultima['total_servicios_gravados']), currency_total_amount)
        sheet.write('E'+str(row+10), float(ultima['total_servicios_exento']), currency_total_amount)
        sheet.write('E'+str(row+11), float(ultima['total_importacion_gravada']), currency_total_amount)
        sheet.write('E'+str(row+12), float(ultima['total_line_peq_contribuyente_exento']), currency_total_amount)
        sheet.write('E'+str(row+13), float(ultima['total_combustible_gravado']), currency_total_amount)
        sheet.write('E'+str(row+14), float(ultima['total_iva_final']), currency_total_amount)
        sheet.write('E'+str(row+15), float(ultima['total_idp_final']), currency_total_amount)
        sheet.write('E'+str(row+16), float(ultima['total_reten_final']), currency_total_amount)
        sheet.write('E'+str(row+17), float(ultima['total_subtotal_final']), currency_total_amount)
        
        # TABLE PARTNER TOTALS
        sheet.merge_range('G'+str(row+6)+':K'+str(row+6), 'TOTALES POR PROVEEDORES', total_table_center)
        sheet.write('G'+str(row+7), 'NO.', total_table_center)
        sheet.write('H'+str(row+7), 'PROVEEDOR', total_table_center)
        sheet.write('I'+str(row+7), 'NIT', total_table_center)
        sheet.write('J'+str(row+7), 'NUM. DE FACTURAS', total_table_center)
        sheet.write('K'+str(row+7), 'TOTAL DE FACTURAS', total_table_center)
        
        line_number = 1
        partner_total = 0
        
        for total_fac in ultima['company_fac_total']: 
            sheet.write('G'+str(row+8), line_number, total_table_center)
            sheet.write('H'+str(row+8), total_fac, total_table_center)
            sheet.write('I'+str(row+8), ultima['company_fac_total'].get(total_fac)[2], total_table_center)
            sheet.write('J'+str(row+8), ultima['company_fac_total'].get(total_fac)[0], total_table_center)
            sheet.write('K'+str(row+8), float(ultima['company_fac_total'].get(total_fac)[1]), currency_total_amount)
            
            row += 1
            line_number += 1
            partner_total += ultima['company_fac_total'].get(total_fac)[1]
        
        sheet.write('G'+str(row+8), '', total_table_center)
        sheet.write('H'+str(row+8), '', total_table_center)
        sheet.write('I'+str(row+8), '**TOTAL**', total_table_center)
        sheet.write('J'+str(row+8), ultima['total_no_fac'], total_table_center)
        sheet.write('K'+str(row+8), float(partner_total), currency_total_amount)