# -*- encoding: utf-8 -*-

import time, datetime
import base64
import io
import logging

from odoo import fields, models, api
from datetime import datetime

_logger = logging.getLogger(__name__)


class ReportPlanillaF987Xls(models.AbstractModel):
    _name = 'report.advanced_reports.report_planilla_f987_xls'
    _description = 'report advanced_reports report_planilla_f987_xls'
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
        row2 = 2
        row3 = 2
        row4 = 2
        row5 = 2
        row6 = 2
        row7 = 2
        row8 = 2
        row9 = 2
        row10 = 2
        row11 = 2
        row12 = 2
        column = 1
        total_final = 0
        now = datetime.now()
        time_now = now.strftime("%Y/%m/%d %H:%M:%S")

        # SHEET AND STYLES
        sheet = workbook.add_worksheet("provInscrito")
        sheet2 = workbook.add_worksheet("provExtranjero")
        sheet3 = workbook.add_worksheet("provExcluido")
        sheet4 = workbook.add_worksheet("Cliente")
        sheet5 = workbook.add_worksheet("Cliente200")
        sheet6 = workbook.add_worksheet("ventasTerceros")
        sheet7 = workbook.add_worksheet("VentasMandatarios")
        sheet8 = workbook.add_worksheet("Acreedor")
        sheet9 = workbook.add_worksheet("Deudor")

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
        # -------------------------Planilla provinscrito------------------------------------------
        result, ultima = self.env['report.advanced_reports.report_planilla_f987'].generate_records_provinscrito(record)

        # SIZE OF COLUMNS
        # WIDTH
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 20)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 30)
        sheet.set_column('F:F', 60)
        sheet.set_column('G:G', 50)
        sheet.set_column('H:H', 40)
        sheet.set_column('I:I', 20)
        sheet.set_column('J:J', 20)
        sheet.set_column('K:K', 20)
        sheet.set_column('L:L', 20)
        sheet.set_column('M:M', 20)
        sheet.set_column('N:N', 20)



        # HEIGTH
        sheet.set_row(1, 30)

        # SET MENU
        sheet.write('B2', 'Fecha Emision', bold)
        sheet.write('C2', 'Mes', bold)
        sheet.write('D2', 'Año', bold)
        sheet.write('E2', 'No. NIT', bold)
        sheet.write('F2', 'Nombre o Razón', bold)
        sheet.write('G2', 'Tipo Doc.', bold)
        sheet.write('H2', 'Clase Doc.', bold)
        sheet.write('I2', 'No. Serie', bold)
        sheet.write('J2', 'No. Doc. Preimpreso', bold)
        sheet.write('K2', 'No. Control Interno', bold)
        sheet.write('L2', 'Monto', bold)
        sheet.write('M2', 'Iva', bold)
        sheet.write('N2', 'Número de anexo', bold)

        if result:
            for line in result:
                sheet.write(row, column, line.get('invoice_date').strftime('%d/%m/%Y') if line.get('invoice_date') else '', no_bold_no)
                sheet.write(row, column + 1, line.get('month'), no_bold_no)
                sheet.write(row, column + 2, line.get('year'), no_bold_no)
                sheet.write(row, column + 3, line.get('vat'), no_bold_no)
                sheet.write(row, column + 4, line.get('partner_name'), no_bold_no)
                sheet.write(row, column + 5, line.get('fe_type'), no_bold_no)
                sheet.write(row, column + 6, line.get('fe_generation'), no_bold_no)
                sheet.write(row, column + 7, line.get('serie'), no_bold_no)
                sheet.write(row, column + 8, line.get('preimpreso'), no_bold_no)
                sheet.write(row, column + 9, line.get('nro_control'), no_bold_no)
                sheet.write(row, column + 10, '{0:,.2f}'.format(line.get('amount')), no_bold_no)
                sheet.write(row, column + 11, '{0:,.2f}'.format(line.get('iva')), no_bold_no)
                sheet.write(row, column + 12, line.get('anexo'), no_bold_no)

                row += 1




        # ---------------------------------planilla provExtranjero----------------------------------

        result_provextranjero, ultima_provextranjero = self.env['report.advanced_reports.report_planilla_f987'].generate_records_provextranjero(record)

        # SIZE OF COLUMNS
        # WIDTH
        sheet2.set_column('B:B', 20)
        sheet2.set_column('C:C', 20)
        sheet2.set_column('D:D', 20)
        sheet2.set_column('E:E', 50)
        sheet2.set_column('F:F', 20)
        sheet2.set_column('G:G', 20)
        sheet2.set_column('H:H', 60)
        sheet2.set_column('I:I', 60)
        sheet2.set_column('J:J', 20)
        sheet2.set_column('K:K', 20)
        sheet2.set_column('L:L', 40)
        sheet2.set_column('M:M', 20)
        sheet2.set_column('N:N', 20)
        sheet2.set_column('O:O', 20)
        sheet2.set_column('P:P', 20)
        sheet2.set_column('Q:Q', 20)

        # HEIGTH
        sheet2.set_row(1, 30)

        # SET MENU
        sheet2.write('B2', 'Fecha Emision', bold)
        sheet2.write('C2', 'Mes', bold)
        sheet2.write('D2', 'Año', bold)
        sheet2.write('E2', 'Concepto de Op.', bold)
        sheet2.write('F2', 'Doc. ID', bold)
        sheet2.write('G2', 'No. Id', bold)
        sheet2.write('H2', 'Nombre o Razon Social', bold)
        sheet2.write('I2', 'Nombre Representante', bold)
        sheet2.write('J2', 'Pais Origen', bold)
        sheet2.write('K2', 'Tel. Contacto', bold)
        sheet2.write('L2', 'Tipo Doc.Importacion', bold)
        sheet2.write('M2', 'Cod. Aduana', bold)
        sheet2.write('N2', 'Num. Doc', bold)
        sheet2.write('O2', 'Monto', bold)
        sheet2.write('P2', 'IVA', bold)
        sheet2.write('Q2', 'Número de anexo', bold)

        if result_provextranjero:
            for line in result_provextranjero:
                sheet2.write(row2, column, line.get('invoice_date').strftime('%d/%m/%Y') if line.get('invoice_date') else '', no_bold_no)
                sheet2.write(row2, column + 1, line.get('month'), no_bold_no)
                sheet2.write(row2, column + 2, line.get('year'), no_bold_no)
                sheet2.write(row2, column + 3, line.get('concept_operation'), no_bold_no)
                sheet2.write(row2, column + 4, line.get('sv_fe_identification_type'), no_bold_no)
                sheet2.write(row2, column + 5, line.get('nro_identification'), no_bold_no)
                sheet2.write(row2, column + 6, line.get('partner_name'), no_bold_no)
                sheet2.write(row2, column + 7, line.get('representante'), no_bold_no)
                sheet2.write(row2, column + 8, line.get('country'), no_bold_no)
                sheet2.write(row2, column + 9, line.get('phone'), no_bold_no)
                sheet2.write(row2, column + 10, line.get('doc_import'), no_bold_no)
                sheet2.write(row2, column + 11, line.get('cod_aduana'), no_bold_no)
                sheet2.write(row2, column + 12, line.get('num_doc'), no_bold_no)
                sheet2.write(row2, column + 13, '{0:,.2f}'.format(line.get('amount')), no_bold_no)
                sheet2.write(row2, column + 14, '{0:,.2f}'.format(line.get('iva')), no_bold_no)
                sheet2.write(row2, column + 15, line.get('anexo'), no_bold_no)

                row2 += 1

        # ---------------------------------planilla provexcluido----------------------------------

        result_provexcluido, ultima_provexcluido = self.env['report.advanced_reports.report_planilla_f987'].generate_records_provexcluido(record)

        # SIZE OF COLUMNS
        # WIDTH
        sheet3.set_column('B:B', 20)
        sheet3.set_column('C:C', 20)
        sheet3.set_column('D:D', 20)
        sheet3.set_column('E:E', 20)
        sheet3.set_column('F:F', 20)
        sheet3.set_column('G:G', 60)
        sheet3.set_column('H:H', 50)
        sheet3.set_column('I:I', 20)
        sheet3.set_column('J:J', 20)
        sheet3.set_column('K:K', 20)
        sheet3.set_column('L:L', 20)
        sheet3.set_column('M:M', 60)
        sheet3.set_column('N:N', 60)
        sheet3.set_column('O:O', 40)
        sheet3.set_column('P:P', 40)
        sheet3.set_column('Q:Q', 40)
        sheet3.set_column('R:R', 40)
        sheet3.set_column('S:S', 20)
        sheet3.set_column('T:T', 20)


        # HEIGTH
        sheet3.set_row(1, 30)

        # SET MENU
        sheet3.write('B2', 'Fecha Emision', bold)
        sheet3.write('C2', 'Mes', bold)
        sheet3.write('D2', 'Año', bold)
        sheet3.write('E2', 'Doc.ID', bold)
        sheet3.write('F2', 'No. ID', bold)
        sheet3.write('G2', 'Nombre', bold)
        sheet3.write('H2', 'Tipo Doc.', bold)
        sheet3.write('I2', 'Num. Doc.', bold)
        sheet3.write('J2', 'Tel.', bold)
        sheet3.write('K2', 'Departamento', bold)
        sheet3.write('L2', 'Municipio', bold)
        sheet3.write('M2', 'Colonia/Barrio/Residencial/Reparto', bold)
        sheet3.write('N2', 'Calle/Av./Pasaje/Poligono', bold)
        sheet3.write('O2', 'No. Casa', bold)
        sheet3.write('P2', 'Apart./Local', bold)
        sheet3.write('Q2', 'Otros Datos Domicilio', bold)
        sheet3.write('R2', 'Correo Electrónico', bold)
        sheet3.write('S2', 'Monto de Op.', bold)
        sheet3.write('T2', 'Número de anexo', bold)

        if result_provexcluido:
            for line in result_provexcluido:
                sheet3.write(row3, column, line.get('invoice_date').strftime('%d/%m/%Y') if line.get('invoice_date') else '', no_bold_no)
                sheet3.write(row3, column + 1, line.get('month'), no_bold_no)
                sheet3.write(row3, column + 2, line.get('year'), no_bold_no)
                sheet3.write(row3, column + 3, line.get('sv_fe_identification_type'), no_bold_no)
                sheet3.write(row3, column + 4, line.get('nro_identification'), no_bold_no)
                sheet3.write(row3, column + 5, line.get('partner_name'), no_bold_no)
                sheet3.write(row3, column + 6, line.get('fe_type'), no_bold_no)
                sheet3.write(row3, column + 7, line.get('num_doc'), no_bold_no)
                sheet3.write(row3, column + 8, line.get('phone'), no_bold_no)
                sheet3.write(row3, column + 9, line.get('department'), no_bold_no)
                sheet3.write(row3, column + 10, line.get('municipality'), no_bold_no)
                sheet3.write(row3, column + 11, line.get('complementary_address'), no_bold_no)
                sheet3.write(row3, column + 12, line.get('street'), no_bold_no)
                sheet3.write(row3, column + 13, line.get('house_number'), no_bold_no)
                sheet3.write(row3, column + 14, line.get('local_apartment'), no_bold_no)
                sheet3.write(row3, column + 15, line.get('address_information'), no_bold_no)
                sheet3.write(row3, column + 16, line.get('email'), no_bold_no)
                sheet3.write(row3, column + 17, '{0:,.2f}'.format(line.get('amount')), no_bold_no)
                sheet3.write(row3, column + 18, line.get('anexo'), no_bold_no)

                row3 += 1



        # ---------------------------------planilla cliente ----------------------------------

        result_cliente, ultima_cliente = self.env['report.advanced_reports.report_planilla_f987'].generate_records_cliente(record)

        # SIZE OF COLUMNS
        # WIDTH
        sheet4.set_column('B:B', 20)
        sheet4.set_column('C:C', 20)
        sheet4.set_column('D:D', 60)
        sheet4.set_column('E:E', 60)
        sheet4.set_column('F:F', 60)
        sheet4.set_column('G:G', 20)
        sheet4.set_column('H:H', 20)
        sheet4.set_column('I:I', 20)
        sheet4.set_column('J:J', 20)
        sheet4.set_column('K:K', 20)
        sheet4.set_column('L:L', 20)


        # HEIGTH
        sheet4.set_row(1, 30)

        # SET MENU
        sheet4.write('B2', 'Doc.ID', bold)
        sheet4.write('C2', 'No. ID', bold)
        sheet4.write('D2', 'Nombre o Razón social', bold)
        sheet4.write('E2', 'Tipo de Doc.', bold)
        sheet4.write('F2', 'No. Doc.', bold)
        sheet4.write('G2', 'Fecha de Emisión del Doc.', bold)
        sheet4.write('H2', 'Mes', bold)
        sheet4.write('I2', 'Año', bold)
        sheet4.write('J2', 'Monto de Op.', bold)
        sheet4.write('K2', 'IVA', bold)
        sheet4.write('L2', 'Número de anexo', bold)

        if result_cliente:
            for line in result_cliente:
                sheet4.write(row4, column, line.get('sv_fe_identification_type'), no_bold_no)
                sheet4.write(row4, column + 1, line.get('nro_identification'), no_bold_no)
                sheet4.write(row4, column + 2, line.get('partner_name'), no_bold_no)
                sheet4.write(row4, column + 3, line.get('fe_type'), no_bold_no)
                sheet4.write(row4, column + 4, line.get('nro_control'), no_bold_no)
                sheet4.write(row4, column + 5,line.get('invoice_date').strftime('%d/%m/%Y') if line.get('invoice_date') else '', no_bold_no)
                sheet4.write(row4, column + 6, line.get('month'), no_bold_no)
                sheet4.write(row4, column + 7, line.get('year'), no_bold_no)
                sheet4.write(row4, column + 8, '{0:,.2f}'.format(line.get('amount')), no_bold_no)
                sheet4.write(row4, column + 9, '{0:,.2f}'.format(line.get('iva')), no_bold_no)
                sheet4.write(row4, column + 10, line.get('anexo'), no_bold_no)
                row4 += 1

        # ---------------------------------planilla cliente200 ----------------------------------

        result_cliente200, ultima_cliente200 = self.env['report.advanced_reports.report_planilla_f987'].generate_records_cliente200(record)

        # SIZE OF COLUMNS
        # WIDTH
        sheet5.set_column('B:B', 20)
        sheet5.set_column('C:C', 20)
        sheet5.set_column('D:D', 20)
        sheet5.set_column('E:E', 20)
        sheet5.set_column('F:F', 20)
        sheet5.set_column('G:G', 20)
        sheet5.set_column('H:H', 20)


        # HEIGTH
        sheet5.set_row(1, 30)

        # SET MENU
        sheet5.write('B2', 'Fecha de Emisión del Doc.', bold)
        sheet5.write('C2', 'Mes', bold)
        sheet5.write('D2', 'Año', bold)
        sheet5.write('E2', 'Registro', bold)
        sheet5.write('F2', 'Monto de Op.', bold)
        sheet5.write('G2', 'IVA', bold)
        sheet5.write('H2', 'Número de anexo', bold)

        if result_cliente200:
            for line in result_cliente200:
                sheet5.write(row5, column, line.get('invoice_date').strftime('%d/%m/%Y') if line.get('invoice_date') else '', no_bold_no)
                sheet5.write(row5, column + 1, line.get('month'), no_bold_no)
                sheet5.write(row5, column + 2, line.get('year'), no_bold_no)
                sheet5.write(row5, column + 3, line.get('quantity'), no_bold_no)
                sheet5.write(row5, column + 4, '{0:,.2f}'.format(line.get('amount')), no_bold_no)
                sheet5.write(row5, column + 5, '{0:,.2f}'.format(line.get('iva')), no_bold_no)
                sheet5.write(row5, column + 6, line.get('anexo'), no_bold_no)
                row5 += 1

        # ---------------------------------planilla  ventas terceros----------------------------------


        # SIZE OF COLUMNS
        # WIDTH
        sheet6.set_column('B:B', 20)
        sheet6.set_column('C:C', 20)
        sheet6.set_column('D:D', 20)
        sheet6.set_column('E:E', 20)
        sheet6.set_column('F:F', 20)
        sheet6.set_column('G:G', 20)
        sheet6.set_column('H:H', 20)
        sheet6.set_column('I:I', 20)
        sheet6.set_column('J:J', 20)
        sheet6.set_column('K:K', 20)
        sheet6.set_column('L:L', 20)
        sheet6.set_column('M:M', 20)
        sheet6.set_column('N:N', 20)

        # HEIGTH
        sheet6.set_row(1, 30)

        # SET MENU
        sheet6.write('B2', 'Fecha Emision', bold)
        sheet6.write('C2', 'Mes', bold)
        sheet6.write('D2', 'Año', bold)
        sheet6.write('E2', 'ID Tributaria', bold)
        sheet6.write('F2', 'Nombre o Razón', bold)
        sheet6.write('G2', 'Tipo Doc.', bold)
        sheet6.write('H2', 'Clase Doc.', bold)
        sheet6.write('I2', 'No. Serie', bold)
        sheet6.write('J2', 'No. Doc. Preimpreso', bold)
        sheet6.write('K2', 'No. Control Interno', bold)
        sheet6.write('L2', 'Monto', bold)
        sheet6.write('M2', 'Iva', bold)
        sheet6.write('N2', 'Número de anexo', bold)

        for line in range(10):
            sheet6.write(row6, column, '', no_bold_no)
            sheet6.write(row6, column + 1, '', no_bold_no)
            sheet6.write(row6, column + 2, '', no_bold_no)
            sheet6.write(row6, column + 3, '', no_bold_no)
            sheet6.write(row6, column + 4, '', no_bold_no)
            sheet6.write(row6, column + 5, '', no_bold_no)
            sheet6.write(row6, column + 6, '', no_bold_no)
            sheet6.write(row6, column + 7, '', no_bold_no)
            sheet6.write(row6, column + 8, '', no_bold_no)
            sheet6.write(row6, column + 9, '', no_bold_no)
            sheet6.write(row6, column + 10, '', no_bold_no)
            sheet6.write(row6, column + 11, '', no_bold_no)
            sheet6.write(row6, column + 12, '', no_bold_no)
            row6 += 1


        # ---------------------------------planilla ventas mandatarios----------------------------------


        # SIZE OF COLUMNS
        # WIDTH
        sheet7.set_column('B:B', 20)
        sheet7.set_column('C:C', 20)
        sheet7.set_column('D:D', 20)
        sheet7.set_column('E:E', 20)
        sheet7.set_column('F:F', 20)
        sheet7.set_column('G:G', 20)
        sheet7.set_column('H:H', 20)
        sheet7.set_column('I:I', 20)
        sheet7.set_column('J:J', 20)
        sheet7.set_column('K:K', 20)
        sheet7.set_column('L:L', 20)
        sheet7.set_column('M:M', 20)
        sheet7.set_column('N:N', 20)
        sheet7.set_column('O:O', 20)

        # HEIGTH
        sheet7.set_row(1, 30)

        # SET MENU
        sheet7.write('B2', 'Fecha Emision', bold)
        sheet7.write('C2', 'Mes', bold)
        sheet7.write('D2', 'Año', bold)
        sheet7.write('E2', 'ID Tributaria', bold)
        sheet7.write('F2', 'Nombre o Razón', bold)
        sheet7.write('G2', 'Tipo Doc.', bold)
        sheet7.write('H2', 'Clase Doc.', bold)
        sheet7.write('I2', 'No. Serie', bold)
        sheet7.write('J2', 'N° Resolución', bold)
        sheet7.write('K2', 'No. Doc. Preimpreso', bold)
        sheet7.write('L2', 'No. Control Interno', bold)
        sheet7.write('M2', 'Monto', bold)
        sheet7.write('N2', 'Iva', bold)
        sheet7.write('O2', 'Número de anexo', bold)

        for line in range(10):
            sheet7.write(row7, column, '', no_bold_no)
            sheet7.write(row7, column + 1, '', no_bold_no)
            sheet7.write(row7, column + 2, '', no_bold_no)
            sheet7.write(row7, column + 3, '', no_bold_no)
            sheet7.write(row7, column + 4, '', no_bold_no)
            sheet7.write(row7, column + 5, '', no_bold_no)
            sheet7.write(row7, column + 6, '', no_bold_no)
            sheet7.write(row7, column + 7, '', no_bold_no)
            sheet7.write(row7, column + 8, '', no_bold_no)
            sheet7.write(row7, column + 9, '', no_bold_no)
            sheet7.write(row7, column + 10, '', no_bold_no)
            sheet7.write(row7, column + 11, '', no_bold_no)
            sheet7.write(row7, column + 12, '', no_bold_no)
            sheet7.write(row7, column + 13, '', no_bold_no)
            row7 += 1


        # ---------------------------------planilla acreedor----------------------------------


        # SIZE OF COLUMNS
        # WIDTH
        sheet8.set_column('B:B', 20)
        sheet8.set_column('C:C', 20)
        sheet8.set_column('D:D', 20)
        sheet8.set_column('E:E', 20)
        sheet8.set_column('F:F', 20)
        sheet8.set_column('G:G', 20)
        sheet8.set_column('H:H', 20)
        sheet8.set_column('I:I', 20)
        sheet8.set_column('J:J', 20)
        sheet8.set_column('K:K', 20)
        sheet8.set_column('L:L', 20)
        sheet8.set_column('M:M', 20)

        # HEIGTH
        sheet8.set_row(1, 30)

        # SET MENU
        sheet8.write('B2', 'Doc. ID', bold)
        sheet8.write('C2', 'No. ID', bold)
        sheet8.write('D2', 'Nombre o Razón Social', bold)
        sheet8.write('E2', 'Tel. Local', bold)
        sheet8.write('F2', 'Tipo Prés.', bold)
        sheet8.write('G2', 'Tipo Gar.', bold)
        sheet8.write('H2', 'Mes', bold)
        sheet8.write('I2', 'Año', bold)
        sheet8.write('J2', 'Monto de Op.', bold)
        sheet8.write('K2', 'Saldo Ant.', bold)
        sheet8.write('L2', 'Saldo Sig.', bold)
        sheet8.write('M2', 'Número de anexo', bold)

        for line in range(10):
            sheet8.write(row8, column, '', no_bold_no)
            sheet8.write(row8, column + 1, '', no_bold_no)
            sheet8.write(row8, column + 2, '', no_bold_no)
            sheet8.write(row8, column + 3, '', no_bold_no)
            sheet8.write(row8, column + 4, '', no_bold_no)
            sheet8.write(row8, column + 5, '', no_bold_no)
            sheet8.write(row8, column + 6, '', no_bold_no)
            sheet8.write(row8, column + 7, '', no_bold_no)
            sheet8.write(row8, column + 8, '', no_bold_no)
            sheet8.write(row8, column + 9, '', no_bold_no)
            sheet8.write(row8, column + 10, '', no_bold_no)
            sheet8.write(row8, column + 11, '', no_bold_no)
            row8 += 1

        # ---------------------------------planilla deudor----------------------------------


        # SIZE OF COLUMNS
        # WIDTH
        sheet9.set_column('B:B', 20)
        sheet9.set_column('C:C', 20)
        sheet9.set_column('D:D', 20)
        sheet9.set_column('E:E', 20)
        sheet9.set_column('F:F', 20)
        sheet9.set_column('G:G', 20)
        sheet9.set_column('H:H', 20)
        sheet9.set_column('I:I', 20)
        sheet9.set_column('J:J', 20)
        sheet9.set_column('K:K', 20)
        sheet9.set_column('L:L', 20)
        sheet9.set_column('M:M', 20)

        # HEIGTH
        sheet9.set_row(1, 30)

        # SET MENU
        sheet9.write('B2', 'Doc. ID', bold)
        sheet9.write('C2', 'No. ID', bold)
        sheet9.write('D2', 'Nombre o Razón Social', bold)
        sheet9.write('E2', 'Tel. Local', bold)
        sheet9.write('F2', 'Tipo Prés.', bold)
        sheet9.write('G2', 'Tipo Gar.', bold)
        sheet9.write('H2', 'Mes', bold)
        sheet9.write('I2', 'Año', bold)
        sheet9.write('J2', 'Monto de Op.', bold)
        sheet9.write('K2', 'Saldo Ant.', bold)
        sheet9.write('L2', 'Saldo Sig.', bold)
        sheet9.write('M2', 'Número de anexo', bold)

        for line in range(10):
            sheet9.write(row9, column, '', no_bold_no)
            sheet9.write(row9, column + 1, '', no_bold_no)
            sheet9.write(row9, column + 2, '', no_bold_no)
            sheet9.write(row9, column + 3, '', no_bold_no)
            sheet9.write(row9, column + 4, '', no_bold_no)
            sheet9.write(row9, column + 5, '', no_bold_no)
            sheet9.write(row9, column + 6, '', no_bold_no)
            sheet9.write(row9, column + 7, '', no_bold_no)
            sheet9.write(row9, column + 8, '', no_bold_no)
            sheet9.write(row9, column + 9, '', no_bold_no)
            sheet9.write(row9, column + 10, '', no_bold_no)
            sheet9.write(row9, column + 11, '', no_bold_no)
            row9 += 1
