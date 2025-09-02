# -*- coding: utf-8 -*-
import time
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import UserError
import csv
import io
import base64
import zipfile


class WizardPlanillaF07(models.TransientModel):
    _name = 'wizard.planilla.f07'
    _description = "Wizard de reporte planilla F-07"

    company_id = fields.Many2one('res.company', 'Empresa', required=True, default=lambda self: self.env.company)
    report_type = fields.Selection([('spreadsheet', 'Planilla')],
                                   string="Tipo de Reporte", required=True, readonly=True)

    def _get_first_day_of_month(self):
        today = date.today()
        first_day_of_month = today.replace(day=1)
        return first_day_of_month
    def _get_last_day_of_month(self):
        today = date.today()
        last_day_of_month = today.replace(day=1) + relativedelta(months=1, days=-1)
        return last_day_of_month

    date_from = fields.Date('Fecha desde', required=True, default=lambda self: self._get_first_day_of_month())
    date_to = fields.Date('Fecha hasta', required=True, default=lambda self: self._get_last_day_of_month())
    # journal_ids = fields.Many2many('account.journal', string="Diarios", required=False)

    def print_report_planilla_f07_xls(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': self.id,
            'model': 'wizard.planilla.f07',
            'form': data,
        }
        return self.env.ref('advanced_reports.action_report_planilla_f07_xls').report_action(self, data=datas)


    def print_report_planilla_f07_csv(self):
        result1, ultima1 = self.env['report.advanced_reports.report_planilla_f07'].generate_records1(self)
        field_mapping1 = self.get_headers_result1()
        result1 = self.rename_headers_result(result1, field_mapping1)
        result2, ultima2 = self.env['report.advanced_reports.report_planilla_f07'].generate_records2(self)
        field_mapping2 = self.get_headers_result2()
        result2 = self.rename_headers_result(result2, field_mapping2)
        result3, ultima3 = self.env['report.advanced_reports.report_planilla_f07'].generate_records3(self)
        field_mapping3 = self.get_headers_result3()
        result3 = self.rename_headers_result(result3, field_mapping3)
        result4, ultima4 = self.env['report.advanced_reports.report_planilla_f07'].generate_records4(self)
        field_mapping4 = self.get_headers_result4()
        result4 = self.rename_headers_result(result4, field_mapping4)
        result5, ultima5 = self.env['report.advanced_reports.report_planilla_f07'].generate_records5(self)
        field_mapping5 = self.get_headers_result5()
        result5 = self.rename_headers_result(result5, field_mapping5)
        result6, ultima6 = self.env['report.advanced_reports.report_planilla_f07'].generate_records6(self)
        field_mapping6 = self.get_headers_result6()
        result6 = self.rename_headers_result(result6, field_mapping6)
        result7, ultima7 = self.env['report.advanced_reports.report_planilla_f07'].generate_records7(self)
        field_mapping7 = self.get_headers_result7()
        result7 = self.rename_headers_result(result7, field_mapping7)
        result8, ultima8 = self.env['report.advanced_reports.report_planilla_f07'].generate_records8(self)
        field_mapping8 = self.get_headers_result8()
        result8 = self.rename_headers_result(result8, field_mapping8)
        result9, ultima9 = self.env['report.advanced_reports.report_planilla_f07'].generate_records9(self)
        field_mapping9 = self.get_headers_result9()
        result9 = self.rename_headers_result(result9, field_mapping9)
        result10, ultima10 = self.env['report.advanced_reports.report_planilla_f07'].generate_records10(self)
        field_mapping10 = self.get_headers_result10()
        result10 = self.rename_headers_result(result10, field_mapping10)
        result11, ultima11 = self.env['report.advanced_reports.report_planilla_f07'].generate_records11(self)
        field_mapping11 = self.get_headers_result11()
        result11 = self.rename_headers_result(result11, field_mapping11)
        result12, ultima12 = self.env['report.advanced_reports.report_planilla_f07'].generate_records12(self)
        field_mapping12 = self.get_headers_result12()
        result12 = self.rename_headers_result(result12, field_mapping12)

        #  Crear buffers en memoria para los CSV
        csv_buffer1 = io.StringIO()
        csv_buffer2 = io.StringIO()
        csv_buffer3 = io.StringIO()
        csv_buffer4 = io.StringIO()
        csv_buffer5 = io.StringIO()
        csv_buffer6 = io.StringIO()
        csv_buffer7 = io.StringIO()
        csv_buffer8 = io.StringIO()
        csv_buffer9 = io.StringIO()
        csv_buffer10 = io.StringIO()
        csv_buffer11 = io.StringIO()
        csv_buffer12 = io.StringIO()

        #  Escribir CSV si tiene datos
        self.write_csv(csv_buffer1, result1, field_mapping1, '1')
        self.write_csv(csv_buffer2, result2, field_mapping2, '2')
        self.write_csv(csv_buffer3, result3, field_mapping3, '3')
        self.write_csv(csv_buffer4, result4, field_mapping4, '4')
        self.write_csv(csv_buffer5, result5, field_mapping5, '5')
        self.write_csv(csv_buffer6, result6, field_mapping6, '6')
        self.write_csv(csv_buffer7, result7, field_mapping7, '7')
        self.write_csv(csv_buffer8, result8, field_mapping8, '8')
        self.write_csv(csv_buffer9, result9, field_mapping9, '9')
        self.write_csv(csv_buffer10, result10, field_mapping10, '10')
        self.write_csv(csv_buffer11, result11, field_mapping11, '11')
        self.write_csv(csv_buffer12, result12, field_mapping12, '12')



        #Crear un buffer en bytes para el ZIP
        zip_buffer = io.BytesIO()

        #  Crear el ZIP en memoria y añadir los CSV
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('planilla_f07_sheet1.csv', csv_buffer1.getvalue())
            zip_file.writestr('planilla_f07_sheet2.csv', csv_buffer2.getvalue())
            zip_file.writestr('planilla_f07_sheet3.csv', csv_buffer3.getvalue())
            zip_file.writestr('planilla_f07_sheet4.csv', csv_buffer4.getvalue())
            zip_file.writestr('planilla_f07_sheet5.csv', csv_buffer5.getvalue())
            zip_file.writestr('planilla_f07_sheet6.csv', csv_buffer6.getvalue())
            zip_file.writestr('planilla_f07_sheet7.csv', csv_buffer7.getvalue())
            zip_file.writestr('planilla_f07_sheet8.csv', csv_buffer8.getvalue())
            zip_file.writestr('planilla_f07_sheet9.csv', csv_buffer9.getvalue())
            zip_file.writestr('planilla_f07_sheet10.csv', csv_buffer10.getvalue())
            zip_file.writestr('planilla_f07_sheet11.csv', csv_buffer11.getvalue())
            zip_file.writestr('planilla_f07_sheet12.csv', csv_buffer12.getvalue())


        # Codificar el ZIP en base64 para crear attachment
        zip_base64 = base64.b64encode(zip_buffer.getvalue())

        # Crear el attachment
        attachment = self.env['ir.attachment'].create({
            'name': 'planilla_f07.zip',
            'type': 'binary',
            'datas': zip_base64,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/zip',
        })

        # Retornar acción para descarga
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=1' % attachment.id,
            'target': 'self',
        }

    def write_csv(self, buffer, result, field_mapping, num_dict):
        if result:
            writer = csv.DictWriter(buffer, fieldnames=result[0].keys())
            # writer.writeheader()
            writer.writerows(result)
        else:
            pass
            # dict = []
            # if num_dict == '1':
            #     dict = self.get_dict_result1()
            # elif num_dict == '2':
            #     dict = self.get_dict_result2()
            # elif num_dict == '3':
            #     dict = self.get_dict_result3()
            # elif num_dict == '4':
            #     dict = self.get_dict_result4()
            # elif num_dict == '5':
            #     dict = self.get_dict_result5()
            # elif num_dict == '6':
            #     dict = self.get_dict_result6()
            # elif num_dict == '7':
            #     dict = self.get_dict_result7()
            # elif num_dict == '8':
            #     dict = self.get_dict_result8()
            # elif num_dict == '9':
            #     dict = self.get_dict_result9()
            # elif num_dict == '10':
            #     dict = self.get_dict_result10()
            # elif num_dict == '11':
            #     dict = self.get_dict_result11()
            # elif num_dict == '12':
            #     dict = self.get_dict_result12()
            # writer = csv.DictWriter(buffer, fieldnames=dict[0].keys())
            # writer.writeheader()
            # writer.writerows(dict)

    def rename_headers_result(self, records, field_mapping):
        renamed = []
        for row in records:
            new_row = {field_mapping.get(k, k): v for k, v in row.items()}
            renamed.append(new_row)
        return renamed

    def get_headers_result1(self):
        field_mapping = {
            'fecha_fact': 'Fecha Emision',
            'clase_doc': 'Clase de Documento',
            'tipo_doc_emitido': 'Tipo de Documento Emitido',
            'numero_resol': 'Numero de Resolucion',
            'serie': 'Serie de Documento',
            'correlativo': 'Numero Correlativo de Documento',
            'numero_control': 'Numero de Control Interno',
            'nrc': 'NIT o NRC del Cliente',
            'cliente': 'Nombre del Cliente',
            'ventas_exentas': 'Ventas exentas',
            'ventas_no_sujetas': 'Ventas no sujetas',
            'ventas_gravadas': 'Ventas gravadas locales',
            'ventas_grabadas_locales': 'Debito Fiscal por ventas gravadas locales',
            'venta_cuenta_terceros': 'Ventas a cuenta de terceros no domiciliados',
            'deb_cuenta_terceros': 'Debito Fiscal por ventas a cuenta de terceros no domiciliados',
            'total': 'Total Ventas',
            'dui': 'DUI del Cliente',
            'tipo_operacion': 'Tipo de Operacion (Renta)',
            'tipo_ingreso': 'Tipo de Ingreso (Renta)',
            'anex': 'Numero de anexo',
        }
        return field_mapping

    def get_headers_result2(self):
        field_mapping = {
            'fecha': 'Fecha',
            'clase_doc': 'Clase de Documento',
            'tipo_doc': 'Tipo de Documento Emitido',
            'num_resolucion': 'Numero de Resolucion',
            'serie_doc': 'Serie de Documento',
            'control_interno_del': 'Numero de Control Interno (del)',
            'control_interno_al': 'Numero de Control Interno (al)',
            'numero_documento_del': 'Numero de documento (del)',
            'numero_documento_al': 'Numero de documento (al)',
            'maq_registradora': 'N° de Maquina registradora',
            'ventas_exentas': 'Ventas Exentas',
            'internas_exentas': 'Ventas Internas Exentas No Sujetas a Proporcionalidad',
            'ventas_no_sujetas': 'Ventas No Sujetas',
            'ventas_grabadas_locales': 'Ventas gravadas locales',
            'exportaciones_centroamericana_int': 'Exportaciones dentro del area Centroamericana',
            'exportaciones_centroamericana_ext': 'Exportaciones fuera del area Centroamericana',
            'exportaciones_servicio': 'Exportaciones de servicios',
            'zonas_francas': 'Ventas a Zonas Francas y DPA (Tasa cero)',
            'terceros_domiciliados': 'Ventas a Cuenta de Terceros No Domiciliados',
            'propina': 'Propina',
            'imp_turismo': 'Impuesto del Turismo',
            'ventas_totales': 'Total Ventas',
            'tipo_operacion': 'Tipo de Operacion (Renta)',
            'tipo_ingreso': 'Tipo de Ingreso (Renta)',
            'anex': 'Numero de anexo',
        }
        return field_mapping

    def get_headers_result3(self):
        field_mapping = {
            'fecha': 'Fecha de emision',
            'clase_doc': 'Clase de documento',
            'tipo_doc': 'Tipo de documento emitido',
            'corralativo_doc': 'Numero Correlativo de Documento',
            'nrc': 'NIT o NRC del proveedor',
            'nombre_proveedor': 'Nombre del proveedor',
            'compras_internas_exentas': 'Compras Internas Exentas',
            'internaciones_exentas': 'Internaciones exentas',
            'importaciones_exentas': 'Importaciones Exentas y/o no sujetas',
            'compras_internas': 'Compras Internas Gravadas',
            'internaciones_grabadas': 'Internaciones Gravadas de bienes',
            'importaciones_grabadas': 'Importaciones gravadas de bienes',
            'importaciones_Servicios': 'Importaciones de servicios gravados',
            'credito_fiscal': 'Credito Fiscal',
            'total_compras': 'Total Compras',
            'dui_proveedor': 'DUI del Proveedor',
            'tipo_operacion': 'Tipo de Operación (Renta)',
            'clasificacion_renta': 'Clasificación (Renta)',
            'sector_renta': 'Sector (Renta)',
            'tipo_costo': 'Tipo de Costo / Gasto (Renta)',
            'anex': 'Numero de Anexo',
        }
        return field_mapping


    def get_headers_result4(self):
        field_mapping = {
            'nrc': 'NIT o NRC del Mandante',
            'nombre_mandante': 'Nombre Mandante',
            'fecha_ccf': 'Fecha de emision CCF o Factura',
            'tipo_documento': 'Tipo de documento',
            'serie_ccf': 'Serie de CCF o Factura',
            'resolucion_ccf': 'Resolucion de CCF o Factura',
            'numero_ccf': 'Numero de CCF o Factura',
            'monto_venta': 'Monto de la venta',
            'debito_fiscal': 'Debito Fiscal',
            'comprobante_liquidacion': 'Serie de Comprobante de Liquidacion',
            'resolucion_comprobante': 'Resolucion de Comprobante de Liquidacion',
            'numero_comprobante': 'Numero de Comprobante de Liquidacion',
            'fecha_comprobante': 'Fecha de emision Comprobante de Liquidacion',
            'dui': 'DUI del Mandante',
            'anex': 'Numero de Anexo',
        }
        return field_mapping

    def get_headers_result5(self):
        field_mapping = {
            'tipo_doc': 'Tipo de documento',
            'number_doc': 'Numero de Documento de Identificacion del proveedor',
            'nombre_proveedor': 'Nombre del proveedor',
            'fecha': 'Fecha de emision',
            'serie': 'Serie',
            'numero_doc': 'Numero de documento emitido',
            'monto_compra': 'Monto de la compra',
            'iva_13': 'Retencion IVA 13%',
            'operacion_renta': 'Tipo de Operacion (Renta)',
            'clasificacion_renta': 'Clasificacion (Renta)',
            'sector': 'Sector (Renta)',
            'tipo_costo': 'Tipo de Costo / Gasto (Renta)',
            'anex': 'Numero de anexo',
        }
        return field_mapping


    def get_headers_result6(self):
        field_mapping = {
            'nit': 'NIT Agente',
            'fecha_emision': 'Fecha de emision',
            'serie': 'Serie',
            'numero_doc': 'Numero de Documento',
            'monto_sujeto': 'Monto sujeto',
            'anticipo_2': 'Monto Anticipo a Cuenta 2%',
            'dui': 'DUI Agente',
            'anex': 'Numero de anexo',
        }
        return field_mapping

    def get_headers_result7(self):
        field_mapping = {
            'nit': 'NIT Agente',
            'fecha_emision': 'Fecha de emision',
            'tipo_doc': 'Tipo de documento',
            'serie': 'Serie',
            'numero_doc': 'Numero de documento',
            'monto_sujeto': 'Monto sujeto',
            'retencion_1': 'Monto Retencion 1%',
            'dui': 'DUI Agente',
            'anex': 'Numero de anexo',
        }
        return field_mapping

    def get_headers_result8(self):
        field_mapping = {
            'nit_agente': 'NIT Agente',
            'fecha_emision': 'Fecha de emision',
            'tipo_doc': 'Tipo de documento',
            'serie': 'Serie',
            'numero_doc': 'Numero de documento',
            'monto_sujeto': 'Monto sujeto',
            'percepcion_1': 'Monto de percepcion 1%',
            'dui_agente': 'DUI Agente',
            'anex': 'Numero de Anexo',
        }
        return field_mapping

    def get_headers_result9(self):
        field_mapping = {
            'nit_sujeto': 'NIT Sujeto',
            'fecha_emision': 'Fecha de emision',
            'tipo_doc': 'Tipo de documento',
            'resolucion': 'Resolucion',
            'serie': 'Serie',
            'numero_documento': 'Numero de documento/Numero de Control',
            'monto_sujeto': 'Monto sujeto',
            'percepcion_1': 'Monto Percepcion 1%',
            'dui_sujeto': 'DUI Sujeto',
            'anex': 'Numero de anexo',
        }
        return field_mapping

    def get_headers_result10(self):
        field_mapping = {
            'nit_sujeto': 'NIT Sujeto',
            'fecha_emision': 'Fecha de emision',
            'tipo_doc': 'Tipo de documento',
            'resolucion': 'Resolucion',
            'serie': 'Serie',
            'numero_documento': 'Numero de documento',
            'monto_sujeto': 'Monto sujeto',
            'retencion_1': 'Monto de la Retencion 1% de IVA',
            'dui_sujeto': 'DUI Sujeto',
            'anex': 'Numero de anexo',
        }
        return field_mapping

    def get_headers_result11(self):
        field_mapping = {
            'nit_sujeto': 'NIT Sujeto',
            'fecha_emision': 'Fecha de emision',
            'resolucion': 'Resolucion',
            'serie': 'Serie',
            'numero_doc': 'Numero de Documento',
            'monto_sujeto': 'Monto sujeto',
            'anticipo_2': 'Monto del Anticipo a Cuenta 2%',
            'dui_sujeto': 'DUI Sujeto',
            'anex': 'Numero de anexo',
        }
        return field_mapping

    def get_headers_result12(self):
        field_mapping = {
            'nit_sujeto': 'NIT Sujeto',
            'fecha_emision': 'Fecha de emision',
            'tipo_doc': 'Tipo de documento',
            'serie': 'Serie',
            'resolution': 'Resolucion',
            'numero_documento': 'Numero de documento',
            'monto_sujeto': 'Monto sujeto',
            'retencion_13': 'Monto Retencion 13%',
            'dui_sujeto': 'DUI Sujeto',
            'anex': 'Numero de anexo',
        }
        return field_mapping


    def get_dict_result1(self):
        dict = []
        line = {
            'fecha_fact': '',
            'clase_doc': '',
            'tipo_doc_emitido': '',
            'numero_resol': '',
            'serie': '',
            'correlativo': '',
            'numero_control': '',
            'nrc': '',
            'cliente': '',
            'ventas_exentas': '',
            'ventas_no_sujetas': '',
            'ventas_gravadas': '',
            'ventas_grabadas_locales': '',
            'venta_cuenta_terceros': '',
            'deb_cuenta_terceros': '',
            'total': '',
            'dui': '',
            'tipo_operacion': '',
            'tipo_ingreso': '',
            'anex': '',
        }
        dict.append(line)
        return dict

    def get_dict_result2(self):
        dict = []
        line = {
            'fecha': '',
            'clase_doc': '',
            'tipo_doc': '',
            'num_resolucion': '',
            'serie_doc': '',
            'control_interno_del': '',
            'control_interno_al': '',
            'numero_documento_del': '',
            'numero_documento_al': '',
            'maq_registradora': '',
            'ventas_exentas': '',
            'internas_exentas': '',
            'ventas_no_sujetas': '',
            'ventas_grabadas_locales': '',
            'exportaciones_centroamericana_int': '',
            'exportaciones_centroamericana_ext': '',
            'exportaciones_servicio': '',
            'zonas_francas': '',
            'terceros_domiciliados': '',
            'ventas_totales': '',
            'tipo_operacion': '',
            'tipo_ingreso': '',
            'anex': '',
        }
        dict.append(line)
        return dict

    def get_dict_result3(self):
        dict = []
        line = {
            'fecha': '',
            'clase_doc': '',
            'tipo_doc': '',
            'corralativo_doc': '',
            'nrc': '',
            'nombre_proveedor': '',
            'compras_internas_exentas': '',
            'internaciones_exentas': '',
            'importaciones_exentas': '',
            'compras_internas': '',
            'internaciones_grabadas': '',
            'importaciones_grabadas': '',
            'importaciones_Servicios': '',
            'credito_fiscal': '',
            'total_compras': '',
            'dui_proveedor': '',
            'tipo_operacion': '',
            'clasificacion_renta': ')',
            'sector_renta': '',
            'tipo_costo': '',
            'anex': '',
        }
        dict.append(line)
        return dict

    def get_dict_result4(self):
        dict = []
        line = {
            'nrc': '',
            'nombre_mandante': '',
            'fecha_ccf': '',
            'tipo_documento': '',
            'serie_ccf': 'a',
            'resolucion_ccf': '',
            'numero_ccf': '',
            'monto_venta': '',
            'debito_fiscal': '',
            'comprobante_liquidacion': '',
            'resolucion_comprobante': '',
            'numero_comprobante': 'n',
            'fecha_comprobante': '',
            'dui': '',
            'anex': '',
        }
        dict.append(line)
        return dict

    def get_dict_result5(self):
        dict = []
        line = {
            'tipo_doc': '',
            'number_doc': '',
            'nombre_proveedor': '',
            'fecha': '',
            'serie': '',
            'numero_doc': '',
            'monto_compra': '',
            'iva_13': '',
            'operacion_renta': '',
            'clasificacion_renta': '',
            'sector': '',
            'tipo_costo': '',
            'anex': '',
        }
        dict.append(line)
        return dict

    def get_dict_result6(self):
        dict = []
        line = {
            'nit': '',
            'fecha_emision': '',
            'serie': '',
            'numero_doc': '',
            'monto_sujeto': '',
            'anticipo_2': '',
            'dui': '',
            'anex': '',
        }
        dict.append(line)
        return dict

    def get_dict_result7(self):
        dict = []
        line = {
            'nit': '',
            'fecha_emision': '',
            'tipo_doc': '',
            'serie': '',
            'numero_doc': '',
            'monto_sujeto': '',
            'retencion_1': '',
            'dui': '',
            'anex': '',
        }
        dict.append(line)
        return dict

    def get_dict_result8(self):
        dict = []
        line = {
            'nit_agente': '',
            'fecha_emision': '',
            'tipo_doc': '',
            'serie': '',
            'numero_doc': '',
            'monto_sujeto': '',
            'percepcion_1': '',
            'dui_agente': '',
        }
        dict.append(line)
        return dict

    def get_dict_result9(self):
        dict = []
        line = {
            'nit_sujeto': '',
            'fecha_emision': '',
            'tipo_doc': '',
            'resolucion': '',
            'serie': '',
            'numero_documento': '',
            'monto_sujeto': '',
            'percepcion_1': '',
            'dui_sujeto': '',
            'anex': '',
        }
        dict.append(line)
        return dict

    def get_dict_result10(self):
        dict = []
        line = {
            'nit_sujeto': '',
            'fecha_emision': '',
            'tipo_doc': '',
            'resolucion': '',
            'serie': '',
            'numero_documento': '',
            'monto_sujeto': '',
            'retencion_1': '',
            'dui_sujeto': '',
            'anex': '',
        }
        dict.append(line)
        return dict

    def get_dict_result11(self):
        dict = []
        line = {
            'nit_sujeto': '',
            'fecha_emision': '',
            'resolucion': '',
            'serie': '',
            'numero_doc': '',
            'monto_sujeto': '',
            'anticipo_2': '',
            'dui_sujeto': '',
            'anex': '',
        }
        dict.append(line)
        return dict

    def get_dict_result12(self):
        dict = []
        line = {
            'nit_sujeto': '',
            'fecha_emision': '',
            'tipo_doc': '',
            'serie': '',
            'resolution': '',
            'numero_documento': '',
            'monto_sujeto': '',
            'retencion_13': '',
            'dui_sujeto': '',
        }
        dict.append(line)
        return dict
