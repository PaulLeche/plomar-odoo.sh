# -*- encoding: utf-8 -*-

import time, datetime
import base64
import io
import logging

from odoo import fields, models, api
from datetime import datetime

_logger = logging.getLogger(__name__)


class ReportPlanillaF07Xls(models.AbstractModel):
    _name = 'report.advanced_reports.report_planilla_f07_xls'
    _description = 'report advanced_reports report_planilla_f07_xls'
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
        column = 0
        total_final = 0
        now = datetime.now()
        time_now = now.strftime("%Y/%m/%d %H:%M:%S")

        # SHEET AND STYLES
        sheet = workbook.add_worksheet("1")
        sheet2 = workbook.add_worksheet("2")
        sheet3 = workbook.add_worksheet("3")
        sheet4 = workbook.add_worksheet("4")
        sheet5 = workbook.add_worksheet("5")
        sheet6 = workbook.add_worksheet("6")
        sheet7 = workbook.add_worksheet("7")
        sheet8 = workbook.add_worksheet("8")
        sheet9 = workbook.add_worksheet("9")
        sheet10 = workbook.add_worksheet("10")
        sheet11 = workbook.add_worksheet("11")
        sheet12 = workbook.add_worksheet("12")
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
        company_nrc = record[0].company_id.partner_id.nrc if record[0].company_id.partner_id.nrc else ""

        # SET DINAMIC HEIGHT OF COLUMNS
        bold.set_text_wrap()
        no_bold_no.set_text_wrap()

        # GET VALUES
        result, ultima = self.env['report.advanced_reports.report_planilla_f07'].generate_records1(record)
        # -------------------------Planilla 1------------------------------------------
        # SIZE OF COLUMNS
        # WIDTH
        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 40)
        sheet.set_column('D:D', 60)
        sheet.set_column('E:E', 60)
        sheet.set_column('F:F', 60)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 20)
        sheet.set_column('I:I', 50)
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
        sheet.set_column('T:T', 20)
        sheet.set_column('U:U', 20)
        sheet.set_column('V:V', 20)


        # HEIGTH
        # sheet.set_row(7, 25)

        # SET MENU
        sheet.write('A2', 'Fecha Emisión', bold)
        sheet.write('B2', 'Clase de Documento', bold)
        sheet.write('C2', 'Tipo de Documento Emitido', bold)
        sheet.write('D2', 'Número de Resolución', bold)
        sheet.write('E2', 'Serie de Documento', bold)
        sheet.write('F2', 'Número Correlativo de Documento', bold)
        sheet.write('G2', 'Número de Control Interno', bold)
        sheet.write('H2', 'NIT o NRC del Cliente', bold)
        sheet.write('I2', 'Nombre del Cliente', bold)
        sheet.write('J2', 'Ventas exentas', bold)
        sheet.write('K2', 'Ventas no sujetas', bold)
        sheet.write('L2', 'Ventas gravadas locales', bold)
        sheet.write('M2', 'Débito Fiscal por ventas gravadas locales', bold)
        sheet.write('N2', 'Ventas a cuenta de terceros no domiciliados', bold)
        sheet.write('O2', 'Débito Fiscal por ventas a cuenta de terceros no domiciliados', bold)
        sheet.write('P2', 'Propina', bold)
        sheet.write('Q2', 'Impuesto del Turismo', bold)
        sheet.write('R2', 'Total Ventas', bold)
        sheet.write('S2', 'DUI del Cliente', bold)
        sheet.write('T2', 'Tipo de Operación (Renta)', bold)
        sheet.write('U2', 'Tipo de Ingreso (Renta)', bold)
        sheet.write('V2', 'Número de anexo', bold)

        if result:
            for line in result:

                sheet.write(row, column, line.get('fecha_fact').strftime('%d/%m/%Y') if line.get('fecha_fact') else '', no_bold_no)
                sheet.write(row, column + 1, line.get('clase_doc'), no_bold_no)
                sheet.write(row, column + 2, line.get('tipo_doc_emitido'), no_bold_no)
                sheet.write(row, column + 3, line.get('numero_resol'), no_bold_no)
                sheet.write(row, column + 4, line.get('serie'), no_bold_no)
                sheet.write(row, column + 5, line.get('correlativo'), no_bold_no)
                sheet.write(row, column + 6, line.get('numero_control'), no_bold_no)
                sheet.write(row, column + 7, line.get('nrc'), no_bold_no)
                sheet.write(row, column + 8, line.get('cliente'), no_bold_no)
                sheet.write(row, column + 9, '{0:,.2f}'.format(line.get('ventas_exentas')), no_bold_no)
                sheet.write(row, column + 10, '{0:,.2f}'.format(line.get('ventas_no_sujetas')), no_bold_no)
                sheet.write(row, column + 11, '{0:,.2f}'.format(line.get('ventas_gravadas')), no_bold_no)
                sheet.write(row, column + 12, '{0:,.2f}'.format(line.get('ventas_grabadas_locales')), no_bold_no)
                sheet.write(row, column + 13, '{0:,.2f}'.format(line.get('venta_cuenta_terceros')), no_bold_no)
                sheet.write(row, column + 14, '{0:,.2f}'.format(line.get('deb_cuenta_terceros')), no_bold_no)
                sheet.write(row, column + 15, '{0:,.2f}'.format(line.get('propina')), no_bold_no)
                sheet.write(row, column + 16, '{0:,.2f}'.format(line.get('imp_turismo')), no_bold_no)
                sheet.write(row, column + 17, '{0:,.2f}'.format(line.get('total')), no_bold_no)
                sheet.write(row, column + 18, line.get('dui'), no_bold_no)
                sheet.write(row, column + 19, line.get('tipo_operacion'), no_bold_no)
                sheet.write(row, column + 20, line.get('tipo_ingreso'), no_bold_no)
                sheet.write(row, column + 21, line.get('anex'), no_bold_no)

                row += 1




        # -------------------------Planilla 2------------------------------------------
        result2, ultima2 = self.env['report.advanced_reports.report_planilla_f07'].generate_records2(record)
        # SIZE OF COLUMNS
        # WIDTH
        sheet2.set_column('A:A', 20)
        sheet2.set_column('B:B', 20)
        sheet2.set_column('C:C', 40)
        sheet2.set_column('D:D', 60)
        sheet2.set_column('E:E', 60)
        sheet2.set_column('F:F', 60)
        sheet2.set_column('G:G', 60)
        sheet2.set_column('H:H', 60)
        sheet2.set_column('I:I', 60)
        sheet2.set_column('J:J', 20)
        sheet2.set_column('K:K', 20)
        sheet2.set_column('L:L', 20)
        sheet2.set_column('M:M', 20)
        sheet2.set_column('N:N', 20)
        sheet2.set_column('O:O', 20)
        sheet2.set_column('P:P', 20)
        sheet2.set_column('Q:Q', 20)
        sheet2.set_column('R:R', 20)
        sheet2.set_column('S:S', 20)
        sheet2.set_column('T:T', 20)
        sheet2.set_column('U:U', 20)
        sheet2.set_column('V:V', 20)
        sheet2.set_column('W:W', 20)
        sheet2.set_column('X:X', 20)
        sheet2.set_column('Y:Y', 20)

        # HEIGTH
        # sheet2.set_row(7, 25)

        # SET MENU
        sheet2.write('A2', 'Fecha', bold)
        sheet2.write('B2', 'Clase de Documento', bold)
        sheet2.write('C2', 'Tipo de Documento Emitido', bold)
        sheet2.write('D2', 'Número de Resolución', bold)
        sheet2.write('E2', 'Serie de Documento', bold)
        sheet2.write('F2', 'Número de Control Interno (del)', bold)
        sheet2.write('G2', 'Número de Control Interno (al)', bold)
        sheet2.write('H2', 'Número de documento (del)', bold)
        sheet2.write('I2', 'Número de documento (al)', bold)
        sheet2.write('J2', 'N° de Máquina registradora ', bold)
        sheet2.write('K2', 'Ventas Exentas', bold)
        sheet2.write('L2', 'Ventas Internas Exentas No Sujetas a Proporcionalidad', bold)
        sheet2.write('M2', 'Ventas No Sujetas', bold)
        sheet2.write('N2', 'Ventas gravadas locales', bold)
        sheet2.write('O2', 'Exportaciones dentro del área Centroamericana', bold)
        sheet2.write('P2', 'Exportaciones fuera del área Centroamericana', bold)
        sheet2.write('Q2', 'Exportaciones de servicios', bold)
        sheet2.write('R2', 'Ventas a Zonas Francas y DPA (Tasa cero)', bold)
        sheet2.write('S2', 'Ventas a Cuenta de Terceros No Domiciliados', bold)
        sheet2.write('T2', 'Propina', bold)
        sheet2.write('U2', 'Impuesto del Turismo', bold)
        sheet2.write('V2', 'Total Ventas', bold)
        sheet2.write('W2', 'Tipo de Operación (Renta)', bold)
        sheet2.write('X2', 'Tipo de Ingreso (Renta)', bold)
        sheet2.write('Y2', 'Número de anexo', bold)



        if result2:
            for line in result2:

                sheet2.write(row2, column, line.get('fecha').strftime('%d/%m/%Y') if line.get('fecha') else '', no_bold_no)
                sheet2.write(row2, column + 1, line.get('clase_doc'), no_bold_no)
                sheet2.write(row2, column + 2, line.get('tipo_doc'), no_bold_no)
                sheet2.write(row2, column + 3, line.get('num_resolucion'), no_bold_no)
                sheet2.write(row2, column + 4, line.get('serie_doc'), no_bold_no)
                sheet2.write(row2, column + 5, line.get('control_interno_del'), no_bold_no)
                sheet2.write(row2, column + 6, line.get('control_interno_al'), no_bold_no)
                sheet2.write(row2, column + 7, line.get('numero_documento_del'), no_bold_no)
                sheet2.write(row2, column + 8, line.get('numero_documento_al'), no_bold_no)
                sheet2.write(row2, column + 9, line.get('maq_registradora'), no_bold_no)
                sheet2.write(row2, column + 10, '{0:,.2f}'.format(line.get('ventas_exentas')), no_bold_no)
                sheet2.write(row2, column + 11, '{0:,.2f}'.format(line.get('internas_exentas')), no_bold_no)
                sheet2.write(row2, column + 12, '{0:,.2f}'.format(line.get('ventas_no_sujetas')), no_bold_no)
                sheet2.write(row2, column + 13, '{0:,.2f}'.format(line.get('ventas_grabadas_locales')), no_bold_no)
                sheet2.write(row2, column + 14, '{0:,.2f}'.format(line.get('exportaciones_centroamericana_int')), no_bold_no)
                sheet2.write(row2, column + 15, '{0:,.2f}'.format(line.get('exportaciones_centroamericana_ext')), no_bold_no)
                sheet2.write(row2, column + 16, '{0:,.2f}'.format(line.get('exportaciones_servicio')),no_bold_no)
                sheet2.write(row2, column + 17, '{0:,.2f}'.format(line.get('zonas_francas')), no_bold_no)
                sheet2.write(row2, column + 18, '{0:,.2f}'.format(line.get('terceros_domiciliados')), no_bold_no)
                sheet2.write(row2, column + 19, '{0:,.2f}'.format(line.get('propina')), no_bold_no)
                sheet2.write(row2, column + 20, '{0:,.2f}'.format(line.get('imp_turismo')), no_bold_no)
                sheet2.write(row2, column + 21, '{0:,.2f}'.format(line.get('ventas_totales')), no_bold_no)
                sheet2.write(row2, column + 22, line.get('tipo_operacion'), no_bold_no)
                sheet2.write(row2, column + 23, line.get('tipo_ingreso'), no_bold_no)
                sheet2.write(row2, column + 24, line.get('anex'), no_bold_no)

                row2 += 1







        # -------------------------Planilla 3------------------------------------------
        result3, ultima3 = self.env['report.advanced_reports.report_planilla_f07'].generate_records3(record)
        # SIZE OF COLUMNS
        # WIDTH
        sheet3.set_column('A:A', 20)
        sheet3.set_column('B:B', 20)
        sheet3.set_column('C:C', 40)
        sheet3.set_column('D:D', 50)
        sheet3.set_column('E:E', 20)
        sheet3.set_column('F:F', 60)
        sheet3.set_column('G:G', 20)
        sheet3.set_column('H:H', 20)
        sheet3.set_column('I:I', 20)
        sheet3.set_column('J:J', 20)
        sheet3.set_column('K:K', 20)
        sheet3.set_column('L:L', 20)
        sheet3.set_column('M:M', 20)
        sheet3.set_column('N:N', 20)
        sheet3.set_column('O:O', 20)
        sheet3.set_column('P:P', 20)
        sheet3.set_column('Q:Q', 50)
        sheet3.set_column('R:R', 20)
        sheet3.set_column('S:S', 50)
        sheet3.set_column('T:T', 50)
        sheet3.set_column('U:U', 20)

        # HEIGTH
        # sheet3.set_row(7, 25)

        # SET MENU
        sheet3.write('A2', 'Fecha de emisión', bold)
        sheet3.write('B2', 'Clase de documento', bold)
        sheet3.write('C2', 'Tipo de documento emitido', bold)
        sheet3.write('D2', 'Número Correlativo de Documento', bold)
        sheet3.write('E2', 'NIT o NRC del proveedor', bold)
        sheet3.write('F2', 'Nombre del proveedor', bold)
        sheet3.write('G2', 'Compras Internas Exentas', bold)
        sheet3.write('H2', 'Internaciones exentas', bold)
        sheet3.write('I2', 'Importaciones Exentas y/o no sujetas', bold)
        sheet3.write('J2', 'Compras Internas Gravadas', bold)
        sheet3.write('K2', 'Internaciones Gravadas de bienes', bold)
        sheet3.write('L2', 'Importaciones gravadas de bienes', bold)
        sheet3.write('M2', 'Importaciones de servicios gravados', bold)
        sheet3.write('N2', 'Crédito Fiscal', bold)
        sheet3.write('O2', 'Total Compras', bold)
        sheet3.write('P2', 'DUI del Proveedor', bold)
        sheet3.write('Q2', 'Tipo de Operación (Renta)', bold)
        sheet3.write('R2', 'Clasificación (Renta)', bold)
        sheet3.write('S2', 'Sector (Renta)', bold)
        sheet3.write('T2', 'Tipo de Costo / Gasto (Renta)', bold)
        sheet3.write('U2', 'Número de Anexo', bold)

        if result3:
            for line in result3:
                sheet3.write(row3, column, line.get('fecha').strftime('%d/%m/%Y') if line.get('fecha') else '', no_bold_no)
                sheet3.write(row3, column + 1, line.get('clase_doc'), no_bold_no)
                sheet3.write(row3, column + 2, line.get('tipo_doc'), no_bold_no)
                sheet3.write(row3, column + 3, line.get('corralativo_doc'), no_bold_no)
                sheet3.write(row3, column + 4, line.get('nrc'), no_bold_no)
                sheet3.write(row3, column + 5, line.get('nombre_proveedor'), no_bold_no)
                sheet3.write(row3, column + 6, '{0:,.2f}'.format(line.get('compras_internas_exentas')), no_bold_no)
                sheet3.write(row3, column + 7, '{0:,.2f}'.format(line.get('internaciones_exentas')), no_bold_no)
                sheet3.write(row3, column + 8, '{0:,.2f}'.format(line.get('importaciones_exentas')), no_bold_no)
                sheet3.write(row3, column + 9, '{0:,.2f}'.format(line.get('compras_internas')), no_bold_no)
                sheet3.write(row3, column + 10, '{0:,.2f}'.format(line.get('internaciones_grabadas')), no_bold_no)
                sheet3.write(row3, column + 11, '{0:,.2f}'.format(line.get('importaciones_grabadas')), no_bold_no)
                sheet3.write(row3, column + 12, '{0:,.2f}'.format(line.get('importaciones_Servicios')), no_bold_no)
                sheet3.write(row3, column + 13, '{0:,.2f}'.format(line.get('credito_fiscal')), no_bold_no)
                sheet3.write(row3, column + 14, '{0:,.2f}'.format(line.get('total_compras')), no_bold_no)
                sheet3.write(row3, column + 15, line.get('dui_proveedor'), no_bold_no)
                sheet3.write(row3, column + 16, line.get('tipo_operacion'), no_bold_no)
                sheet3.write(row3, column + 17, line.get('clasificacion_renta'), no_bold_no)
                sheet3.write(row3, column + 18, line.get('sector_renta'), no_bold_no)
                sheet3.write(row3, column + 19, line.get('tipo_costo'), no_bold_no)
                sheet3.write(row3, column + 20, line.get('anex'), no_bold_no)

                row3 += 1








        # -------------------------Planilla 4------------------------------------------
        # result4, ultima4 = self.env['report.advanced_reports.report_planilla_f07'].generate_records4(record)
        result4 = False
        # SIZE OF COLUMNS
        # WIDTH
        sheet4.set_column('A:A', 20)
        sheet4.set_column('B:B', 60)
        sheet4.set_column('C:C', 20)
        sheet4.set_column('D:D', 20)
        sheet4.set_column('E:E', 20)
        sheet4.set_column('F:F', 60)
        sheet4.set_column('G:G', 60)
        sheet4.set_column('H:H', 20)
        sheet4.set_column('I:I', 20)
        sheet4.set_column('J:J', 20)
        sheet4.set_column('K:K', 20)
        sheet4.set_column('L:L', 20)
        sheet4.set_column('M:M', 20)
        sheet4.set_column('N:N', 20)
        sheet4.set_column('O:O', 20)

        # HEIGTH
        sheet4.set_row(7, 25)

        # SET MENU
        sheet4.write('A2', 'NIT o NRC del Mandante', bold)
        sheet4.write('B2', 'Nombre Mandante', bold)
        sheet4.write('C2', 'Fecha de emisión CCF o Factura', bold)
        sheet4.write('D2', 'Tipo de documento', bold)
        sheet4.write('E2', 'Serie de CCF o Factura', bold)
        sheet4.write('F2', 'Resolución de CCF o Factura', bold)
        sheet4.write('G2', 'Número de CCF o Factura', bold)
        sheet4.write('H2', 'Monto de la venta', bold)
        sheet4.write('I2', 'Débito Fiscal', bold)
        sheet4.write('J2', 'Serie de Comprobante de Liquidación', bold)
        sheet4.write('K2', 'Resolución de Comprobante de Liquidación', bold)
        sheet4.write('L2', 'Número de Comprobante de Liquidación', bold)
        sheet4.write('M2', 'Fecha de emisión Comprobante de Liquidación', bold)
        sheet4.write('N2', 'DUI del Mandante', bold)
        sheet4.write('O2', 'Número de Anexo', bold)


        if result4:
            for line in result4:

                sheet4.write(row4, column, line.get('nrc'), no_bold_no)
                sheet4.write(row4, column + 1, line.get('nombre_mandante'), no_bold_no)
                sheet4.write(row4, column + 2, line.get('fecha_ccf').strftime('%d/%m/%Y') if line.get('fecha_ccf') else '', no_bold_no)
                sheet4.write(row4, column + 3, line.get('tipo_documento'), no_bold_no)
                sheet4.write(row4, column + 4, line.get('serie_ccf'), no_bold_no)
                sheet4.write(row4, column + 5, line.get('resolucion_ccf'), no_bold_no)
                sheet4.write(row4, column + 6, line.get('numero_ccf'), no_bold_no)
                sheet4.write(row4, column + 7, '{0:,.2f}'.format(line.get('monto_venta')), no_bold_no)
                sheet4.write(row4, column + 8, '{0:,.2f}'.format(line.get('debito_fiscal')), no_bold_no)
                sheet4.write(row4, column + 9, line.get('comprobante_liquidacion'), no_bold_no)
                sheet4.write(row4, column + 10, line.get('resolucion_comprobante'), no_bold_no)
                sheet4.write(row4, column + 11, line.get('numero_comprobante'), no_bold_no)
                sheet4.write(row4, column + 12, line.get('fecha_comprobante'), no_bold_no)
                sheet4.write(row4, column + 13, line.get('dui'), no_bold_no)
                sheet4.write(row4, column + 14, line.get('anex'), no_bold_no)

                row4 += 1




        # -------------------------Planilla 5------------------------------------------
        result5, ultima5 = self.env['report.advanced_reports.report_planilla_f07'].generate_records5(record)
        # SIZE OF COLUMNS
        # WIDTH
        sheet5.set_column('A:A', 20)
        sheet5.set_column('B:B', 40)
        sheet5.set_column('C:C', 60)
        sheet5.set_column('D:D', 20)
        sheet5.set_column('E:E', 60)
        sheet5.set_column('F:F', 60)
        sheet5.set_column('G:G', 20)
        sheet5.set_column('H:H', 20)
        sheet5.set_column('I:I', 40)
        sheet5.set_column('J:J', 40)
        sheet5.set_column('K:K', 40)
        sheet5.set_column('L:L', 50)
        sheet5.set_column('M:M', 20)


        # HEIGTH
        # sheet5.set_row(7, 25)

        # SET MENU
        sheet5.write('A2', 'Tipo de documento', bold)
        sheet5.write('B2', 'Número de Documento de Identificación del proveedor', bold)
        sheet5.write('C2', 'Nombre del proveedor', bold)
        sheet5.write('D2', 'Fecha de emisión', bold)
        sheet5.write('E2', 'Serie', bold)
        sheet5.write('F2', 'Número de documento emitido', bold)
        sheet5.write('G2', 'Monto de la compra', bold)
        sheet5.write('H2', 'Retención IVA 13%', bold)
        sheet5.write('I2', 'Tipo de Operación (Renta)', bold)
        sheet5.write('J2', 'Clasificación (Renta)', bold)
        sheet5.write('K2', 'Sector (Renta)', bold)
        sheet5.write('L2', 'Tipo de Costo / Gasto (Renta)', bold)
        sheet5.write('M2', 'Número de anexo', bold)

        if result5:
            for line in result5:

                sheet5.write(row5, column, line.get('tipo_doc'), no_bold_no)
                sheet5.write(row5, column + 1, line.get('number_doc'), no_bold_no)
                sheet5.write(row5, column + 2, line.get('nombre_proveedor'), no_bold_no)
                sheet5.write(row5, column + 3, line.get('fecha').strftime('%d/%m/%Y') if line.get('fecha') else '',no_bold_no)
                sheet5.write(row5, column + 4, line.get('serie'), no_bold_no)
                sheet5.write(row5, column + 5, line.get('numero_doc'), no_bold_no)
                sheet5.write(row5, column + 6, '{0:,.2f}'.format(line.get('monto_compra')), no_bold_no)
                sheet5.write(row5, column + 7, '{0:,.2f}'.format(line.get('iva_13')), no_bold_no)
                sheet5.write(row5, column + 8, line.get('operacion_renta'), no_bold_no)
                sheet5.write(row5, column + 9, line.get('clasificacion_renta'), no_bold_no)
                sheet5.write(row5, column + 10, line.get('sector'), no_bold_no)
                sheet5.write(row5, column + 11, line.get('tipo_costo'), no_bold_no)
                sheet5.write(row5, column + 12, line.get('anex'), no_bold_no)


                row5 += 1






        # -------------------------Planilla 6------------------------------------------
        # result6, ultima6 = self.env['report.advanced_reports.report_planilla_f07'].generate_records6(record)
        # SIZE OF COLUMNS
        # WIDTH
        result6 = False
        sheet6.set_column('A:A', 20)
        sheet6.set_column('B:B', 20)
        sheet6.set_column('C:C', 20)
        sheet6.set_column('D:D', 60)
        sheet6.set_column('E:E', 20)
        sheet6.set_column('F:F', 20)
        sheet6.set_column('G:G', 20)
        sheet6.set_column('H:H', 20)

        # HEIGTH
        # sheet6.set_row(7, 25)

        # SET MENU
        sheet6.write('A2', 'NIT Agente', bold)
        sheet6.write('B2', 'Fecha de emisión', bold)
        sheet6.write('C2', 'Serie', bold)
        sheet6.write('D2', 'Número de Documento', bold)
        sheet6.write('E2', 'Monto sujeto', bold)
        sheet6.write('F2', 'Monto Anticipo a Cuenta 2%', bold)
        sheet6.write('G2', 'DUI Agente', bold)
        sheet6.write('H2', 'Número de anexo', bold)

        if result6:
            for line in result6:

                sheet6.write(row6, column, line.get('nit'), no_bold_no)
                sheet6.write(row6, column + 1, line.get('fecha_emision').strftime('%d/%m/%Y') if line.get('fecha_emision') else '', no_bold_no)
                sheet6.write(row6, column + 2, line.get('serie'), no_bold_no)
                sheet6.write(row6, column + 3, line.get('numero_doc'), no_bold_no)
                sheet6.write(row6, column + 4, '{0:,.2f}'.format(line.get('monto_sujeto')), no_bold_no)
                sheet6.write(row6, column + 5, '{0:,.2f}'.format(line.get('anticipo_2')), no_bold_no)
                sheet6.write(row6, column + 6, line.get('dui'), no_bold_no)
                sheet6.write(row6, column + 7, line.get('anex'), no_bold_no)

                row6 += 1





        # -------------------------Planilla 7------------------------------------------
        # result7, ultima7 = self.env['report.advanced_reports.report_planilla_f07'].generate_records7(record)
        # SIZE OF COLUMNS
        # WIDTH
        result7 = False
        sheet7.set_column('A:A', 20)
        sheet7.set_column('B:B', 20)
        sheet7.set_column('C:C', 50)
        sheet7.set_column('D:D', 50)
        sheet7.set_column('E:E', 60)
        sheet7.set_column('F:F', 20)
        sheet7.set_column('G:G', 20)
        sheet7.set_column('H:H', 20)
        sheet7.set_column('I:I', 20)

        # HEIGTH
        # sheet7.set_row(7, 25)

        # SET MENU
        sheet7.write('A2', 'NIT Agente', bold)
        sheet7.write('B2', 'Fecha de emisión', bold)
        sheet7.write('C2', 'Tipo de documento', bold)
        sheet7.write('D2', 'Serie', bold)
        sheet7.write('E2', 'Número de documento', bold)
        sheet7.write('F2', 'Monto sujeto', bold)
        sheet7.write('G2', 'Monto Retención 1%', bold)
        sheet7.write('H2', 'DUI Agente', bold)
        sheet7.write('I2', 'Número de anexo', bold)


        if result7:
            for line in result7:

                sheet7.write(row7, column, line.get('nit'), no_bold_no)
                sheet7.write(row7, column + 1, line.get('fecha_emision').strftime('%d/%m/%Y') if line.get('fecha_emision') else '', no_bold_no)
                sheet7.write(row7, column + 2, line.get('tipo_doc'), no_bold_no)
                sheet7.write(row7, column + 3, line.get('serie'), no_bold_no)
                sheet7.write(row7, column + 4, line.get('numero_doc'), no_bold_no)
                sheet7.write(row7, column + 5, '{0:,.2f}'.format(line.get('monto_sujeto')), no_bold_no)
                sheet7.write(row7, column + 6, '{0:,.2f}'.format(line.get('retencion_1')), no_bold_no)
                sheet7.write(row7, column + 7, line.get('dui'), no_bold_no)
                sheet7.write(row7, column + 8, line.get('anex'), no_bold_no)

                row7 += 1



        # -------------------------Planilla 8------------------------------------------
        result8, ultima8 = self.env['report.advanced_reports.report_planilla_f07'].generate_records8(record)
        # SIZE OF COLUMNS
        # WIDTH
        sheet8.set_column('A:A', 20)
        sheet8.set_column('B:B', 20)
        sheet8.set_column('C:C', 50)
        sheet8.set_column('D:D', 20)
        sheet8.set_column('E:E', 50)
        sheet8.set_column('F:F', 20)
        sheet8.set_column('G:G', 20)
        sheet8.set_column('H:H', 20)
        sheet8.set_column('I:I', 20)

        # HEIGTH
        # sheet8.set_row(7, 25)

        # SET MENU
        sheet8.write('A2', 'NIT Agente', bold)
        sheet8.write('B2', 'Fecha de emisión', bold)
        sheet8.write('C2', 'Tipo de documento', bold)
        sheet8.write('D2', 'Serie', bold)
        sheet8.write('E2', 'Número de documento', bold)
        sheet8.write('F2', 'Monto sujeto', bold)
        sheet8.write('G2', 'Monto de percepción 1%', bold)
        sheet8.write('H2', 'DUI Agente', bold)
        sheet8.write('I2', 'Número de Anexo', bold)


        if result8:
            for line in result8:

                sheet8.write(row8, column, line.get('nit_agente'), no_bold_no)
                sheet8.write(row8, column + 1, line.get('fecha_emision').strftime('%d/%m/%Y') if line.get('fecha_emision') else '', no_bold_no)
                sheet8.write(row8, column + 2, line.get('tipo_doc'), no_bold_no)
                sheet8.write(row8, column + 3, line.get('serie'), no_bold_no)
                sheet8.write(row8, column + 4, line.get('numero_doc'), no_bold_no)
                sheet8.write(row8, column + 5, '{0:,.2f}'.format(line.get('monto_sujeto')), no_bold_no)
                sheet8.write(row8, column + 6, '{0:,.2f}'.format(line.get('percepcion_1')), no_bold_no)
                sheet8.write(row8, column + 7, line.get('dui_agente'), no_bold_no)
                sheet8.write(row8, column + 8, line.get('anex'), no_bold_no)

                row8 += 1





        # -------------------------Planilla 9------------------------------------------
        result9, ultima9 = self.env['report.advanced_reports.report_planilla_f07'].generate_records9(record)
        # SIZE OF COLUMNS
        # WIDTH
        sheet9.set_column('A:A', 20)
        sheet9.set_column('B:B', 20)
        sheet9.set_column('C:C', 50)
        sheet9.set_column('D:D', 50)
        sheet9.set_column('E:E', 20)
        sheet9.set_column('F:F', 50)
        sheet9.set_column('G:G', 20)
        sheet9.set_column('H:H', 20)
        sheet9.set_column('I:I', 20)
        sheet9.set_column('J:J', 20)


        # HEIGTH
        # sheet9.set_row(7, 25)

        # SET MENU
        sheet9.write('A2', 'NIT Sujeto', bold)
        sheet9.write('B2', 'Fecha de emisión', bold)
        sheet9.write('C2', 'Tipo de documento', bold)
        sheet9.write('D2', 'Resolución', bold)
        sheet9.write('E2', 'Serie', bold)
        sheet9.write('F2', 'Número de documento/Número de Control', bold)
        sheet9.write('G2', 'Monto sujeto', bold)
        sheet9.write('H2', 'Monto Percepción 1%', bold)
        sheet9.write('I2', 'DUI Sujeto', bold)
        sheet9.write('J2', 'Número de anexo', bold)

        if result9:
            for line in result9:

                sheet9.write(row9, column, line.get('nit_sujeto'), no_bold_no)
                sheet9.write(row9, column + 1, line.get('fecha_emision').strftime('%d/%m/%Y') if line.get('fecha_emision') else '', no_bold_no)
                sheet9.write(row9, column + 2, line.get('tipo_doc'), no_bold_no)
                sheet9.write(row9, column + 3, line.get('resolucion'), no_bold_no)
                sheet9.write(row9, column + 4, line.get('serie'), no_bold_no)
                sheet9.write(row9, column + 5, line.get('numero_documento'), no_bold_no)
                sheet9.write(row9, column + 6, '{0:,.2f}'.format(line.get('monto_sujeto')), no_bold_no)
                sheet9.write(row9, column + 7, '{0:,.2f}'.format(line.get('percepcion_1')), no_bold_no)
                sheet9.write(row9, column + 8, line.get('dui_sujeto'), no_bold_no)
                sheet9.write(row9, column + 9, line.get('anex'), no_bold_no)

                row9 += 1




        # -------------------------Planilla 10------------------------------------------
        result10, ultima10 = self.env['report.advanced_reports.report_planilla_f07'].generate_records10(record)
        # SIZE OF COLUMNS
        # WIDTH
        sheet10.set_column('A:A', 20)
        sheet10.set_column('B:B', 20)
        sheet10.set_column('C:C', 50)
        sheet10.set_column('D:D', 50)
        sheet10.set_column('E:E', 20)
        sheet10.set_column('F:F', 60)
        sheet10.set_column('G:G', 20)
        sheet10.set_column('H:H', 20)
        sheet10.set_column('I:I', 20)
        sheet10.set_column('J:J', 20)

        # HEIGTH
        # sheet10.set_row(7, 25)

        # SET MENU
        sheet10.write('A2', 'NIT Sujeto', bold)
        sheet10.write('B2', 'Fecha de emisión', bold)
        sheet10.write('C2', 'Tipo de documento', bold)
        sheet10.write('D2', 'Resolución', bold)
        sheet10.write('E2', 'Serie', bold)
        sheet10.write('F2', 'Número de documento', bold)
        sheet10.write('G2', 'Monto sujeto', bold)
        sheet10.write('H2', 'Monto de la Retención 1% de IVA', bold)
        sheet10.write('I2', 'DUI Sujeto', bold)
        sheet10.write('J2', 'Número de anexo', bold)


        if result10:
            for line in result10:

                sheet10.write(row10, column, line.get('nit_sujeto'), no_bold_no)
                sheet10.write(row10, column + 1, line.get('fecha_emision').strftime('%d/%m/%Y') if line.get('fecha_emision') else '', no_bold_no)
                sheet10.write(row10, column + 2, line.get('tipo_doc'), no_bold_no)
                sheet10.write(row10, column + 3, line.get('resolucion'), no_bold_no)
                sheet10.write(row10, column + 4, line.get('serie'), no_bold_no)
                sheet10.write(row10, column + 5, line.get('numero_documento'), no_bold_no)
                sheet10.write(row10, column + 6, '{0:,.2f}'.format(line.get('monto_sujeto')), no_bold_no)
                sheet10.write(row10, column + 7, '{0:,.2f}'.format(line.get('retencion_1')), no_bold_no)
                sheet10.write(row10, column + 8, line.get('dui_sujeto'), no_bold_no)
                sheet10.write(row10, column + 9, line.get('anex'), no_bold_no)

                row10 += 1



        # -------------------------Planilla 11------------------------------------------
        result11, ultima11 = self.env['report.advanced_reports.report_planilla_f07'].generate_records11(record)
        # SIZE OF COLUMNS
        # WIDTH
        sheet11.set_column('A:A', 20)
        sheet11.set_column('B:B', 20)
        sheet11.set_column('C:C', 50)
        sheet11.set_column('D:D', 20)
        sheet11.set_column('E:E', 50)
        sheet11.set_column('F:F', 20)
        sheet11.set_column('G:G', 20)
        sheet11.set_column('H:H', 20)
        sheet11.set_column('I:I', 20)

        # HEIGTH
        # sheet11.set_row(7, 25)

        # SET MENU
        sheet11.write('A2', 'NIT Sujeto', bold)
        sheet11.write('B2', 'Fecha de emisión', bold)
        sheet11.write('C2', 'Resolución', bold)
        sheet11.write('D2', 'Serie', bold)
        sheet11.write('E2', 'Número de Documento', bold)
        sheet11.write('F2', 'Monto sujeto', bold)
        sheet11.write('G2', 'Monto del Anticipo a Cuenta 2%', bold)
        sheet11.write('H2', 'DUI Sujeto', bold)
        sheet11.write('I2', 'Número de anexo', bold)

        if result11:
            for line in result11:
                sheet11.write(row11, column, line.get('nit_sujeto'), no_bold_no)
                # sheet11.write(row11, column + 1,line.get('fecha_emision').strftime('%d/%m/%Y') if line.get('fecha_emision') else '',no_bold_no)
                sheet11.write(row11, column + 1, line.get('fecha_emision').strftime('%d/%m/%Y') if line.get('fecha_emision') else '', no_bold_no)
                sheet11.write(row11, column + 2, line.get('resolucion'), no_bold_no)
                sheet11.write(row11, column + 3, line.get('serie'), no_bold_no)
                sheet11.write(row11, column + 4, line.get('numero_doc'), no_bold_no)
                sheet11.write(row11, column + 5, '{0:,.2f}'.format(line.get('monto_sujeto')), no_bold_no)
                sheet11.write(row11, column + 6, '{0:,.2f}'.format(line.get('anticipo_2')), no_bold_no)
                sheet11.write(row11, column + 7, line.get('dui_sujeto'), no_bold_no)
                sheet11.write(row11, column + 8, line.get('anex'), no_bold_no)

                row11 += 1




        # -------------------------Planilla 12------------------------------------------
        result12, ultima12 = self.env['report.advanced_reports.report_planilla_f07'].generate_records12(record)
        # SIZE OF COLUMNS
        # WIDTH
        sheet12.set_column('A:A', 20)
        sheet12.set_column('B:B', 20)
        sheet12.set_column('C:C', 50)
        sheet12.set_column('D:D', 20)
        sheet12.set_column('E:E', 20)
        sheet12.set_column('F:F', 60)
        sheet12.set_column('G:G', 20)
        sheet12.set_column('H:H', 20)
        sheet12.set_column('I:I', 20)
        sheet12.set_column('J:J', 20)

        # HEIGTH
        sheet12.set_row(7, 25)

        # SET MENU
        sheet12.write('A2', 'NIT Sujeto', bold)
        sheet12.write('B2', 'Fecha de emisión', bold)
        sheet12.write('C2', 'Tipo de documento', bold)
        sheet12.write('D2', 'Serie', bold)
        sheet12.write('E2', 'Resolución', bold)
        sheet12.write('F2', 'Número de documento', bold)
        sheet12.write('G2', 'Monto sujeto', bold)
        sheet12.write('H2', 'Monto Retención 13%', bold)
        sheet12.write('I2', 'DUI Sujeto', bold)
        sheet12.write('J2', 'Número de anexo', bold)

        if result12:
            for line in result12:
                sheet12.write(row12, column, line.get('nit_sujeto'), no_bold_no)
                # sheet12.write(row12, column + 1,line.get('fecha_emision').strftime('%d/%m/%Y') if line.get('fecha_emision') else '',no_bold_no)
                sheet12.write(row12, column + 1, line.get('fecha_emision'), no_bold_no)
                sheet12.write(row12, column + 2, line.get('tipo_doc'), no_bold_no)
                sheet12.write(row12, column + 3, line.get('serie'), no_bold_no)
                sheet12.write(row12, column + 4, line.get('resolution'), no_bold_no)
                sheet12.write(row12, column + 5, line.get('numero_documento'), no_bold_no)
                sheet12.write(row12, column + 6, '{0:,.2f}'.format(line.get('monto_sujeto')), no_bold_no)
                sheet12.write(row12, column + 7, '{0:,.2f}'.format(line.get('retencion_13')), no_bold_no)
                sheet12.write(row12, column + 8, line.get('dui_sujeto'), no_bold_no)
                sheet12.write(row12, column + 9, line.get('anex'), no_bold_no)

                row12 += 1











