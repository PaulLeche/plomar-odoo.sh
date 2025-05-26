# -*- coding: utf-8 -*-

import base64
import logging
import urllib.request

import requests
from pytz import timezone
import json
from xml.etree import ElementTree as ET

from datetime import datetime, date, timedelta
from dateutil.parser import parse
from io import BytesIO

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement
import re
import base64

_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except:
    raise UserError(_("run Command: 'pip install num2words'"))

TYPE_SERVICE = [
    ('01', 'Bienes'),
    ('02', 'Servicios'),
    ('03', 'Ambos'),
    ('04', 'Otros'),
]

TYPE_PAYMENT = [
    ('01', 'Contado'),
    ('02', 'Crédito'),
    ('03', 'Otro'),
]

TYPE_PAYMENT_METHOD = [
    ('01', 'Billetes y monedas'),
    ('02', 'Tarjeta Débito'),
    ('03', 'Tarjeta Crédito'),
    ('04', 'Cheque'),
    ('05', 'Transferencia_ Depósito Bancario'),
    ('08', 'Dinero electrónico'),
    ('09', 'Monedero electrónico'),
    ('11', 'Bitcoin'),
    ('12', 'Otras Criptomonedas'),
    ('13', 'Cuentas por pagar del receptor'),
    ('14', 'Giro bancario'),
    ('99', 'Otros')
]

TYPE_TERM = [
    ('01', 'Días'),
    ('02', 'Meses'),
    ('03', 'Años')
]

TYPE_GENERATION = [
    ('01', 'Físico'),
    ('02', 'Electrónico')
]

TYPE_INVALIDATION = [
    ('02', 'Rescindir de la operación realizada'),
]

class AccountMove(models.Model):
    _inherit = 'account.move'
    

    ##CAMPO Y FUNCION PARA OBTENER EL CORRELATIVO DEL ULTIMO PAGO
    last_payment_sequence = fields.Char(
        string="Último Pago Correlativo",
        compute="_compute_last_payment_sequence"
    )

    @api.depends('payment_state', 'amount_residual')
    def _compute_last_payment_sequence(self):
        for record in self:
            _logger.info("**************************************RECORD*************************************")
                
            if record.payment_state in ('in_payment', 'paid','partial'):
                last_payment = self.env['account.payment'].search([
                        ('ref', '=', record.name),
                        ('state', '=', 'posted')
                    ], order='id desc', limit=1)
                record.last_payment_sequence = last_payment.name or ''
            else:
                record.last_payment_sequence = ''

    def get_num2words(self, amount, currency_name):
        words = num2words(amount, lang='es', to='currency')
        words = words.capitalize()
        if currency_name == 'USD':
            if 'céntimo' in words:
                words = words.replace("euros", "Dólares")
                result = words.replace("céntimo", "centavo")
            else:
                result = words.replace("euros", " Dólares Exactos")
        else:
            if 'céntimo' in words:
                words = words.replace("euros", "Dólar")
                result = words.replace("céntimo", "centavo")
            else:
                result = words.replace("euros", " Dólares Exacto")

        return result

    def action_print_fel(self):
        return self.env.ref('l10n_sv_fe.invoice_fel_templates').report_action(self)

    @api.model
    def default_get(self, default_fields):
        values = super(AccountMove, self).default_get(default_fields)
        values['fe_type'] = '03' if values.get('move_type', False) == 'out_refund' else '01'

        return values

    # fields list
    fe_type = fields.Selection(related="journal_id.fe_type", string='Tipo', store=True)
    fact_info = fields.Text(store=True)
    prev_move_info = fields.Text(readonly=True, store=True)
    uuid_code = fields.Char(string='UUID', readonly=True, copy=False,tracking=True)

    date_certification = fields.Char(string='Fecha DTE', readonly=True, copy=False)
    numero_control = fields.Char(string='Número de control', readonly=True, copy=False)
    fe_cf = fields.Boolean('Consumidor Final', default=False, help='Si se desea poder generar Notas de Remisión esta opción deberá estar desactivada, Activado para generar una factura de consumidor final')
    fe_payment = fields.Selection(TYPE_PAYMENT, string='Tipo Pago', store=True, help='Tipo de pago.')
    
    fe_pay_method = fields.Selection(TYPE_PAYMENT_METHOD, string='Método de Pago', store=True, help='Seleccione el método de pago')
    fe_term = fields.Selection(TYPE_TERM, string='Plazo', store=True)
    fe_period = fields.Integer(string='Periodo', store=True)
    fe_generation = fields.Selection(TYPE_GENERATION, string='Tipo Generación', store=True)

    fe_pdf = fields.Char(string='PDF')
    invalidation_type = fields.Selection(TYPE_INVALIDATION, string='Tipo Invalidación FEL', store=True, copy=False, default="02", required=True, help='Deberá de colocar un motivo para la invalidación')
    motivo_invalidacion = fields.Text(string="Motivo Invalidación", copy=False)
    
    tribute_fe = fields.Many2one('tribute.fel', string='Tributo', help='Tributo al que corresponde el producto, requerido en comprobantes de crédito fiscal, nota de remisión, notas de crédito y débito ')
    fe_incoterm = fields.Many2one('export.incoterm', string='Código Incoterms', help='Requerido para facturas de exportación')
    fe_recinto = fields.Many2one('export.recinto', string='Recinto Fiscal', help='Requerido para facturas de exportación')
    fe_regimen = fields.Many2one('export.regimen', string='Régimen', help='Requerido para facturas de exportación')
    
    fe_export_services = fields.Selection(TYPE_SERVICE, string='Tipo de producto para exportación', store=True, help='Cuando crea una factura de exportación, los productos deben de corresponder a este nuevo campo.')
    fe_active = fields.Boolean(string="Active FE", related="journal_id.fe_active")

    # campo para guardar el sello de recepcion
    receipt_stamp = fields.Char(string="Sello de recepción")

    def action_post(self):
        if self.move_type in ['out_invoice', 'out_refund']:
            if not self.invoice_date:
                self.invoice_date = date.today()

            if self.invoice_date < (date.today() - timedelta(days=5)):
                raise UserError(_('Error. Date cannot exceed 5 days'))
        rec = super(AccountMove, self).action_post()
        
        if self.fe_active and not self.uuid_code:
            self.json_create()

        return rec

    def _get_address_error(self):
        if self.partner_id.fe_address_dep == False:
            raise ValidationError("Se debe colocar la información del departamento del cliente para continuar.")

        if self.partner_id.fe_address_mun == False:
            raise ValidationError("Se debe colocar la información del municipio del cliente para continuar.")

        if self.partner_id.complement_address == False:
            raise ValidationError("Se debe colocar la información del dirección complementaria del cliente para continuar.")

    def _get_pago_documento(self, total_items):
        pago = {}
        if int(self.fe_payment) == 1:
            pago = {
                "tipo": "01",
                "monto": round(total_items, 4)
            }
        _logger.info("TOTAL _get_pago_documento: %s", pago)

        if int(self.fe_payment) == 2:
            pago = {
                "tipo": "02",
                "monto": round(total_items, 4),
                "plazo": self.fe_term,
                "periodo": self.fe_period
            }

        if int(self.fe_payment) == 3:
            pago = {
                "tipo": "03",
                "monto": round(total_items, 4)
            }

        return pago

    def _get_document_number(self):
        numero_documento = ""

        if self.partner_id and self.partner_id.identification_type:
            # NIT
            if self.partner_id.identification_type == '36':
                numero_documento = self.partner_id.vat

            # DUI  
            if self.partner_id.identification_type == '13':
                numero_documento = self.partner_id.dui_field[:-1] + '-' + self.partner_id.dui_field[-1]

            # OTRO    
            if self.partner_id.identification_type == '37':
                numero_documento = self.partner_id.other_field

            # PASAPORTE
            if self.partner_id.identification_type == '03':
                numero_documento = self.partner_id.passport_field
            
            # CARNET DE RESIDENTE
            if self.partner_id.identification_type == '02':
                numero_documento = self.partner_id.carnet_residente_field

        return numero_documento

    def _get_user_document_number(self):
        numero_documento = ""
        user = self.env.user
        # if self.user_id and self.user_id.identification_type:
        if user and user.identification_type:
            # NIT
            if user.identification_type == '36':
                numero_documento = user.vat

            # DUI  
            if user.identification_type == '13':
                numero_documento = user.dui_field

            # OTRO    
            if user.identification_type == '37':
                numero_documento = user.other_field

            # PASAPORTE
            if user.identification_type == '03':
                numero_documento = user.passport_field
            
            # CARNET DE RESIDENTE
            if user.identification_type == '02':
                numero_documento = user.carnet_residente_field

        return numero_documento

    @api.onchange('journal_id')
    def _onchange_journal_id_to_type(self):
        for order in self:
            if order.journal_id:
                order.fe_type = order.journal_id.fe_type

    def _sign_invoice(self, cancel=False, xml_cancel=False):
        headers = {'Content-Type': 'application/json'}
        URL = self.env['ir.config_parameter'].sudo().get_param('url.sign.webservice.fe')
        payloads = self.company_id._get_sign_token()
        payloads.update({
            "codigo": str(self.journal_id.fe_establishment_id.fe_code) if self.journal_id.fe_establishment_id else "0",
            "archivo": xml_cancel if cancel else self.arch_xml,
            "es_anulacion": "S" if cancel else "N"
        })

        response = requests.post(url=URL, json=payloads, headers=headers)
        data = response.json()

        return data['archivo']

    def send_invoice(self):
        if self.fe_active:
            return

    def get_pdf(self):
        URL = self.fe_pdf
        return {
            'type': 'ir.actions.act_url',
            'url': URL,
            'download': True,
            'target': 'new',
        }

    def get_json(self):
        url = "https://certificador.infile.com.sv/api/v1/reporte/reporte_documento"
        params = {
            'uuid': self.uuid_code,
            'formato': 'json',
        }
        try:
            # Realiza la solicitud al enlace
            response = requests.get(url, params=params)
            response.raise_for_status()

            # Convierte el contenido en un archivo descargable
            json_content = response.json()
            file_content = base64.b64encode(response.content)
            attachment = self.env['ir.attachment'].create({
                'name': 'factura_'+self.name+'.json',
                'type': 'binary',
                'datas': file_content,
                'res_model': 'reporte.documento',
                'res_id': self.id,
                'mimetype': 'application/json',
            })

            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'self',
            }

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error al descargar el JSON: {e}")


    def cancel_dte(self):
        if self.invalidation_type and self.motivo_invalidacion:
            usr_json = str(self.company_id.fe_user)
            key_json = str(self.company_id.fe_key_webservice)

            headers = {
                "Content-Type": "application/json",
                "usuario": usr_json,
                "llave": key_json,
            }

            urltest = "https://certificador.infile.com.sv/api/v1/certificacion/test/documento/invalidacion"
            urlprod = "https://certificador.infile.com.sv/api/v1/certificacion/prod/documento/invalidacion"
            user = self.env.user
            json_invalidation_body = {
                "invalidacion": {
                    "establecimiento": self.journal_id.fe_establishment_id.fe_code,
                    "uuid": self.uuid_code,
                    "tipo_anulacion": int(self.invalidation_type),
                    "motivo": self.motivo_invalidacion,
                    "responsable": {
                        "nombre": user.name,
                        "tipo_documento": user.identification_type,
                    },
                    "solicitante": {
                        "nombre": user.name,
                        "tipo_documento":user.identification_type,
                        "correo": user.login
                    }
                }
            }
            _logger.info("**********JSON INVALIDACION*********")
            _logger.info(json_invalidation_body)

            json_invalidation_body["invalidacion"]["responsable"]["numero_documento"] = self._get_user_document_number()
            json_invalidation_body["invalidacion"]["solicitante"]["numero_documento"] = self._get_user_document_number()
            self.message_post(subject='FEL', body="Generando cancelacion Factura Electronica FEL",attachments=[('cancelacion-Factura.json', str(json_invalidation_body))])
            json_data = json.dumps(json_invalidation_body)
            URL = urlprod if self.company_id.fe_mode_prod else urltest
            respuesta = requests.post(URL, json_data, headers=headers)
            como_json = respuesta.json()

            if como_json['ok'] == False:
                raise UserError(str(como_json['errores']))
            else:
                return self.button_cancel()
            self.get_pdf()
        else:
            raise ValidationError("Rellena el motivo de invalidación para poder cancelar este documento.")

    def button_cancel(self):
        for record in self:
            if not record.fe_active:
                continue

        return super(AccountMove, self).button_cancel()

    def action_ccf(self):
        # Crea una copia del movimiento contable
        duplicated_move = self.copy()

        # Cambia el diario de la copia al diario con el código "CCF"
        new_journal = self.env['account.journal'].search([('code', '=', 'CCF')])
        if new_journal:
            duplicated_move.journal_id = new_journal.id

        # Abre el formulario de la copia para que el usuario pueda editarla si es necesario
        action = self.env.ref('account.action_move_journal_line').read()[0]
        action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
        action['res_id'] = duplicated_move.id

        return action

    def json_create(self):
        has_advance = False
        observations = ''
        if self.uuid_code:
            return
        
        usr_json = str(self.company_id.fe_user)
        key_json = str(self.company_id.fe_key_webservice)
        identifier = f"DTE{self.id}"

        headers = {
            "Content-Type": "application/json",
            "usuario": usr_json,
            "llave": key_json,
            "identificador" : identifier
        }

        # SET TOTAL
        total_items = self.amount_total
        _logger.info("T*****************************************")
        _logger.info("TOTAL: %s", str(total_items))
        json_body = {}

        # DTE FACTURA
        if int(self.fe_type) == 1:
            # for item in self.invoice_line_ids:
            #     if not item.tax_ids:
            #         raise UserError('Para validar una factura es necesario agregar el impuesto')

            date_anticipo = ''
            total_anticipo = 0.0
            json_body = {
                "documento": {
                    "tipo_dte": str(self.fe_type),
                    "establecimiento": self.journal_id.fe_establishment_id.fe_code,
                    "condicion_pago": int(self.fe_payment),
                    "pagos": [],
                    "items": []
                }
            }

            # AGREGAR PAGO EN JSON
            pago = self._get_pago_documento(total_items)
            json_body["documento"]["pagos"].append(pago)

            for item in self.invoice_line_ids.filtered(lambda l: l.display_type != 'line_section'):
                total_discount = (item.price_unit * item.quantity) - item.price_subtotal
                price_unit = self.get_price_unit(item)
                if 'anticipo' in item.name.lower() and item.quantity < 0.0:
                    total_anticipo += price_unit
                    date_anticipo = self.extract_date(item.name)
                    has_advance = True
                else:
                    item_data = {
                        "tipo": int(item.product_id.fe_services),
                        "cantidad": item.quantity,
                        "unidad_medida": int(item.product_id.fe_unidad_medida_id.code),
                        "descuento": round(total_discount, 6) if total_discount > 0 else 0.0,
                        "descripcion": item.name,
                        # "precio_unitario": round(((item.price_total + total_discount) / item.quantity), 6)
                        "precio_unitario": price_unit
                    }
                    if not item.tax_ids:
                        item_data.update({'tipo_venta': '2'})
                    if any('Exento IVA' in tax.name for tax in item.tax_ids):
                        item_data.update({'tipo_venta': '3'})
                    json_body["documento"]["items"].append(item_data)
            if has_advance == True:
                json_body["documento"]["descuento_gravadas"] = round(total_anticipo, 2)
                observations = 'El anticipo fue emitido el día' + ' ' + date_anticipo + ' ' + 'por valor a' + ' ' + str(round(total_anticipo, 2)) + self.currency_id.symbol
            if total_items >= 1095:
                self.fe_cf == False
            else:
                self.fe_cf == True

            if self.fe_cf == False:
                receptor_info = {
                    "tipo_documento": self.partner_id.identification_type,
                    "numero_documento": self._get_document_number(),
                    "nombre": self.partner_id.name,
                    "correo": self.partner_id.email
                }

                json_body["documento"]["receptor"] = receptor_info
            if self.partner_id.type_consumer_taxp in ['consumer', 'taxpayer']:
                receptor_info = {
                    "tipo_documento": self.partner_id.identification_type,
                    "numero_documento": self._get_document_number(),
                    "nombre": self.partner_id.name,
                    "correo": self.partner_id.email
                }
                json_body["documento"]["receptor"] = receptor_info

        # dte comprobante de credito fiscal
        if int(self.fe_type) == 3:
            # validacion de impuestos
            for item in self.invoice_line_ids.filtered(lambda l: l.display_type != 'line_section'):
                if not item.tax_ids:
                    raise UserError('Para validar un comprobante de crédito fiscal es necesario agregar el impuesto')

            tributo_porcentaje = 0.13
            total_items = self.amount_total

            json_body = {}
            self.fe_type = '03'

            # esto es para cuando el ccf viene de un documento relacionado, de una factura.
            if self.fact_info != 0:
                # prepara el str para convertirlo a json
                response_raw = self.fact_info.replace("'", '"')
                response_raw = response_raw.strip()
                response_raw = response_raw.replace(" ", "")

                response_raw = response_raw.replace("None", "null")
                response_raw = response_raw.replace('True', 'true')
                prev_move_data = json.loads(self.prev_move_info)

                # convierte a json
                _logger.info("Contenido de response_raw antes de decodificar JSON: %s", str(response_raw))
                response_data = json.loads(response_raw)

                # pago contado
                json_body = {
                    "documento": {
                        "tipo_dte": str(self.fe_type),
                        "establecimiento": self.journal_id.fe_establishment_id.fe_code,
                        "condicion_pago": int(self.fe_payment),
                        "pagos": [],
                        "items": [],
                    }
                }

                # AGREGAR PAGO EN JSON
                pago = self._get_pago_documento(total_items)
                json_body["documento"]["pagos"].append(pago)

                # receptor assignment
                receptor_info = {
                    "numero_documento": self._get_document_number(),
                    "nrc": self.partner_id.nrc,
                    "nombre": self.partner_id.name,
                    "codigo_actividad": self.partner_id.fe_code_activity.code,
                }
                json_body["documento"]["receptor"] = receptor_info

                # informacion de remitente
                self._get_address_error()
                direccion = {
                    "departamento": str(self.partner_id.fe_address_dep.code),
                    "municipio": str(self.partner_id.fe_address_mun.code_muni),
                    "complemento": self.partner_id.complement_address,
                }
                # agrega al json la direccion y el correo
                json_body["documento"]["receptor"]["direccion"] = direccion
                json_body["documento"]["receptor"]["correo"] = self.partner_id.email
                is_anticipo = any('anticipo' in line.name.lower() and line.quantity < 0.0 for line in self.invoice_line_ids)
                if is_anticipo:
                    result = []
                    date_anticipo = ''
                    total_anticipo = 0.0
                    for item in self.invoice_line_ids.filtered(lambda l: l.display_type != 'line_section'):
                        tributo_item = (item.price_total - item.price_subtotal)
                        total_discount = (item.price_unit * item.quantity) - item.price_subtotal
                        if 'anticipo' in item.name.lower() and item.quantity < 0.0:
                            price_comprovante = abs(round(item.price_unit, 6))
                            total_anticipo += price_comprovante
                            date_anticipo = self.extract_date(item.name)
                            has_advance = True
                        else:
                            item_data = {
                                "tipo": int(item.product_id.fe_services),
                                "cantidad": item.quantity,
                                "unidad_medida": int(item.product_id.fe_unidad_medida_id.code),
                                "descuento": round(total_discount, 6) if total_discount > 0 else 0.0,
                                "descripcion": item.name,
                                "precio_unitario": round(item.price_unit, 6),
                            }
                            if self.fe_type == '05':
                                item_data.update({'numero_documento': str(None)})
                            if not len(item.tax_ids) > 0:
                                item_data.update({'tipo_venta': '2'})
                            if any('Exento IVA' in tax.name for tax in item.tax_ids):
                                item_data.update({'tipo_venta': '3'})
                            if any('IVA por Pagar' in tax.name for tax in item.tax_ids):
                                tributos = []
                                for tax in item.tax_ids:
                                    if 'IVA por Pagar' in tax.name:
                                        line_tribute = {'codigo': '20',
                                                        'monto': (item.price_unit * item.quantity) * (tax.amount / 100)}
                                        tributos.append(line_tribute)
                                item_data.update({'tributos': tributos})
                            result.append(item_data)
                    json_body["documento"]["items"] = result
                else:
                    json_body["documento"]["items"] = self.get_inf_items()
                if has_advance == True:
                    json_body["documento"]["descuento_gravadas"] = round(total_anticipo, 2)
                    observations = 'El anticipo fue emitido el día' + ' ' + date_anticipo + ' ' + 'por valor a' + ' ' + str(round(total_anticipo, 2)) + self.currency_id.symbol

            else:
                json_body = {
                    "documento": {
                        "tipo_dte": str(self.fe_type),
                        "establecimiento": self.journal_id.fe_establishment_id.fe_code,
                        "condicion_pago": int(self.fe_payment),
                        "pagos": [],
                        "items": [],
                    }
                }

                # AGREGAR PAGO EN JSON
                pago = self._get_pago_documento(total_items)
                json_body["documento"]["pagos"].append(pago)

                # receptor assignment
                receptor_info = {
                    "numero_documento": self._get_document_number(),
                    "nrc": self.partner_id.nrc,
                    "nombre": self.partner_id.name,
                    "codigo_actividad": self.partner_id.fe_code_activity.code,
                }

                json_body["documento"]["receptor"] = receptor_info

                # informacion de remitente
                self._get_address_error()
                direccion = {
                    "departamento": str(self.partner_id.fe_address_dep.code),
                    "municipio": str(self.partner_id.fe_address_mun.code_muni),
                    "complemento": self.partner_id.complement_address,
                }
                # agrega al json la direccion y el correo
                json_body["documento"]["receptor"]["direccion"] = direccion
                json_body["documento"]["receptor"]["correo"] = self.partner_id.email
                is_anticipo = any('anticipo' in line.name.lower() and line.quantity < 0.0 for line in self.invoice_line_ids)
                if is_anticipo:
                    result = []
                    date_anticipo = ''
                    total_anticipo = 0.0
                    for item in self.invoice_line_ids.filtered(lambda l: l.display_type != 'line_section'):
                        tributo_item = (item.price_total - item.price_subtotal)
                        total_discount = (item.price_unit * item.quantity) - item.price_subtotal
                        if 'anticipo' in item.name.lower() and item.quantity < 0.0:
                            price_comprovante = abs(round(item.price_unit, 6))
                            total_anticipo += price_comprovante
                            date_anticipo = self.extract_date(item.name)
                            has_advance = True
                        else:
                            item_data = {
                                "tipo": int(item.product_id.fe_services),
                                "cantidad": item.quantity,
                                "unidad_medida": int(item.product_id.fe_unidad_medida_id.code),
                                "descuento": round(total_discount, 6) if total_discount > 0 else 0.0,
                                "descripcion": item.name,
                                "precio_unitario": round(item.price_unit, 6),
                            }
                            if self.fe_type == '05':
                                item_data.update({'numero_documento': str(None)})
                            if not len(item.tax_ids) > 0:
                                item_data.update({'tipo_venta': '2'})
                            if any('Exento IVA' in tax.name for tax in item.tax_ids):
                                item_data.update({'tipo_venta': '3'})
                            if any('IVA por Pagar' in tax.name for tax in item.tax_ids):
                                tributos = []
                                for tax in item.tax_ids:
                                    if 'IVA por Pagar' in tax.name:
                                        line_tribute = {'codigo': '20',
                                                        'monto': (item.price_unit * item.quantity) * (tax.amount / 100)}
                                        tributos.append(line_tribute)
                                item_data.update({'tributos': tributos})
                            result.append(item_data)
                    json_body["documento"]["items"] = result
                else:
                    json_body["documento"]["items"] = self.get_inf_items()
                if has_advance == True:
                    json_body["documento"]["descuento_gravadas"] = round(total_anticipo, 2)
                    observations = 'El anticipo fue emitido el día' + ' ' + date_anticipo + ' ' + 'por valor a' + ' ' + str(round(total_anticipo, 2)) + self.currency_id.symbol

        # dte nota de credito
        if int(self.fe_type) == 5:

            for item in self.invoice_line_ids:
                if not item.tax_ids:
                    raise UserError('Para validar un comprobante de crédito fiscal es necesario agregar el impuesto')

            tributo_porcentaje = 0.13

            if self.fact_info != 0:
                # Prepara el string para convertirlo a JSON
                _logger.info(str(self.fact_info))
                # Expresión regular para encontrar comillas dobles entre 2 letras. 
                # Esto es necesario una vez que se sustituyan todas las comillas simples por dobles
                # Y conservar el nombre de clientes como D'QUISA,S.A.DE C.V.
                patron = r"(?<=[a-zA-Z0-9\"\\])\"(?=[a-zA-Z0-9\"\\])"
                response_raw = (self.fact_info.replace("'", '"')
                                .strip()
                                .replace(" ", "")
                                .replace("None", "null")
                                .replace('True', 'true')
                                .replace('False', 'false'))  # Agregando también la conversión de False
                response_raw = re.sub(patron, "'", response_raw)
                _logger.info("Inspecting response_raw: %s", type(response_raw))
                _logger.info("Inspecting response_raw: %s", response_raw)  # Añadir esto para depuración

                try:
                    prev_move_data = json.loads(self.prev_move_info)
                    response_data = json.loads(response_raw)
                except json.JSONDecodeError as e:
                    _logger.error("Error al decodificar el JSON: %s", e)
                    raise

                # Inicializa la estructura del documento JSON
                json_body = {
                    "documento": {
                        "tipo_dte": str(self.fe_type),
                        "establecimiento": self.journal_id.fe_establishment_id.fe_code,
                        "condicion_pago": int(self.fe_payment),
                        "fecha_emision": self.invoice_date.strftime("%Y-%m-%d"),
                        'hora_emision': datetime.now(timezone('America/El_Salvador')).strftime("%H:%M:%S"),
                        "pagos": [],
                        "items": []
                    }
                }

                # Agregar pago al JSON
                pago = self._get_pago_documento(total_items)
                json_body["documento"]["pagos"].append(pago)

                # Agregar ítems al JSON
                try:
                    codigo_generacion = response_data['respuesta']['codigoGeneracion']
                    json_body["documento"]["items"] = self.get_inf_items(codigo_generacion)
                except KeyError:
                    _logger.error("Error al obtener código de generación de la respuesta")
                    raise ValueError("Error al obtener código de generación de la respuesta")

                # Agregar documentos relacionados
                try:
                    fecha_emision_str = response_data['respuesta']['fechaEmision']
                    fecha_emision = datetime.strptime(fecha_emision_str, "%Y-%m-%d%H:%M:%S").strftime("%Y-%m-%d")
                    documentos_relacionados = [{
                        "tipo_documento": str(prev_move_data['documento']['tipo_dte']),
                        "tipo_generacion": int(self.fe_generation),
                        "numero_documento": str(codigo_generacion),
                        "fecha_emision": fecha_emision,
                    }]
                    json_body["documento"]["documentos_relacionados"] = documentos_relacionados
                except (KeyError, ValueError):
                    _logger.error("Error al obtener información de documentos relacionados")
                    raise ValueError("Error al obtener información de documentos relacionados")

                # Obtener dirección del remitente
                self._get_address_error()
                direccion = {
                    "departamento": str(self.partner_id.fe_address_dep.code),
                    "municipio": str(self.partner_id.fe_address_mun.code_muni),
                    "complemento": self.partner_id.complement_address,
                }

                # Información del receptor
                receptor_info = {
                    "numero_documento": self._get_document_number(),
                    "nrc": self.partner_id.nrc,
                    "nombre": self.partner_id.name,
                    "codigo_actividad": self.partner_id.fe_code_activity.code,
                    "direccion": direccion,
                    "correo": self.partner_id.email
                }

                json_body["documento"]["receptor"] = receptor_info

                # agrega al json la direccion y el correo
                json_body["documento"]["receptor"]["direccion"] = direccion
                json_body["documento"]["receptor"]["correo"] = self.partner_id.email

        # DTE Nota de Debito
        if int(self.fe_type) == 6:
            for item in self.invoice_line_ids:
                if not item.tax_ids:
                    raise UserError('Para validar un comprobante de crédito fiscal es necesario agregar el impuesto')

            tributo_porcentaje = 0.13
            
            if self.fact_info != 0:
                # prepara el str para convertirlo a json
                response_raw = self.fact_info.replace("'", '"')
                response_raw = response_raw.strip()
                response_raw = response_raw.replace(" ", "")

                response_raw = response_raw.replace("None", "null")
                response_raw = response_raw.replace('True', 'true')
                prev_move_data = json.loads(self.prev_move_info)

                # convierte a json
                response_data = json.loads(response_raw)

                # pago contado
                json_body = {
                    "documento": {
                        "tipo_dte": str(self.fe_type),
                        "establecimiento": self.journal_id.fe_establishment_id.fe_code,
                        "condicion_pago": int(self.fe_payment),
                        "pagos": [],
                        "items": []
                    }
                }

                # AGREGAR PAGO EN JSON
                pago = self._get_pago_documento(total_items)
                json_body["documento"]["pagos"].append(pago)

                json_body["documento"]["items"] = self.get_inf_items()

                fecha_emision = datetime.strptime(str(response_data['respuesta']['fechaEmision']), "%Y-%m-%d%H:%M:%S")

                # related document
                documentos_relacionados = [{
                    "tipo_documento": str(prev_move_data['documento']['tipo_dte']),
                    "tipo_generacion": int(self.fe_generation),
                    "numero_documento": str(response_data['respuesta']['codigoGeneracion']),
                    "fecha_emision": str(fecha_emision),
                }]

                json_body["documento"]["documentos_relacionados"] = documentos_relacionados

                # informacion de remitente
                self._get_address_error()
                direccion = {
                    "departamento": str(self.partner_id.fe_address_dep.code),
                    "municipio": str(self.partner_id.fe_address_mun.code_muni),
                    "complemento": self.partner_id.complement_address,
                }

                # receptor assignment
                receptor_info = {
                    "numero_documento": self._get_document_number(),
                    "nrc": self.partner_id.nrc,
                    "nombre": self.partner_id.name,
                    "codigo_actividad": self.partner_id.fe_code_activity.code,
                }

                json_body["documento"]["receptor"] = receptor_info

                # agrega al json la direccion y el correo
                json_body["documento"]["receptor"]["direccion"] = direccion
                json_body["documento"]["receptor"]["correo"] = self.partner_id.email

        # dte Factura de exportacion
        if int(self.fe_type) == 11:
            date_anticipo = ''
            total_anticipo = 0.0
            for item in self.invoice_line_ids.filtered(lambda l: l.display_type != 'line_section'):
                if not item.tax_ids:
                    raise UserError('Para validar una factura de exportación es necesario agregar el impuesto')
            json_body = {
                "documento": {
                    "tipo_dte": str(self.fe_type),
                    "establecimiento": self.journal_id.fe_establishment_id.fe_code,
                    "tipo_item_exportacion": int(self.fe_export_services),
                    "condicion_pago": int(self.fe_payment),
                    "pagos": [],
                    "items": []
                }
            }
            # AGREGAR PAGO EN JSON
            pago = self._get_pago_documento(total_items)
            json_body["documento"]["pagos"].append(pago)
            for item in self.invoice_line_ids.filtered(lambda l: l.display_type != 'line_section'):
                total_discount = (item.price_unit * item.quantity) - item.price_subtotal
                if 'anticipo' in item.name.lower() and item.quantity < 0.0:
                    price_export = abs(round((((item.price_total + total_discount) / item.quantity)), 6))
                    total_anticipo += price_export
                    date_anticipo = self.extract_date(item.name)
                    has_advance = True
                else:
                    item_data = {
                        "tipo": int(item.product_id.fe_services),
                        "cantidad": item.quantity,
                        "unidad_medida": int(item.product_id.fe_unidad_medida_id.code),
                        "descuento": round(total_discount, 6) if total_discount > 0 else 0.0,
                        "descripcion": item.name,
                        "precio_unitario": round((((item.price_total + total_discount) / item.quantity)), 6)
                    }

                    json_body["documento"]["items"].append(item_data)
            if has_advance == True:
                json_body["documento"]["descuento_global"] = round(total_anticipo, 2)
                observations = 'El anticipo fue emitido el día' + ' ' + date_anticipo + ' ' + 'por valor a' + ' ' + str(round(total_anticipo, 2)) + self.currency_id.symbol
            # receptor assignment
            receptor_info = {
                "tipo_documento": self.partner_id.identification_type,
                "numero_documento": self._get_document_number(),
                "nombre": self.partner_id.name,
                "descripcion_actividad": self.partner_id.fe_code_activity.activity_name,
                "codigo_pais": str(self.partner_id.fe_country.code_country),
                "complemento": self.partner_id.complement_address,
                "tipo_persona": int(self.partner_id.tipo_persona),
                "correo": self.partner_id.email
            }
            json_body["documento"]["receptor"] = receptor_info
            
            # agregar regimen y recinto de ser necesario
            if int(self.fe_export_services) != 2:
                json_body["documento"]["codigo_incoterm"] = self.fe_incoterm.code_incoterm
                json_body["documento"]["recinto_fiscal"] = self.fe_recinto.code_recinto
                json_body["documento"]["regimen"] = self.fe_regimen.code_regimen

        # DTE Comprobante de sujeto excluido
        if int(self.fe_type) == 14:
            for item in self.invoice_line_ids:
                if not item.tax_ids:
                    raise UserError('Para validar una factura es necesario agregar el impuesto')

            json_body = {
                "documento": {
                    "tipo_dte": str(self.fe_type),
                    "establecimiento": self.journal_id.fe_establishment_id.fe_code,
                    "condicion_pago": int(self.fe_payment),
                    "pagos": [],
                    "items": []
                }
            }

            # AGREGAR PAGO EN JSON
            pago = self._get_pago_documento(total_items)
            json_body["documento"]["pagos"].append(pago)

            for item in self.invoice_line_ids:
                total_discount = (item.price_unit * item.quantity) - item.price_subtotal

                item_data = {
                    "tipo": int(item.product_id.fe_services),
                    "cantidad": item.quantity,
                    "unidad_medida": int(item.product_id.fe_unidad_medida_id.code),
                    "descuento": round(total_discount, 6),
                    "descripcion": item.name,
                    "precio_unitario": round(item.price_unit, 6)
                }

                json_body["documento"]["items"].append(item_data)

            receptor_info = {
                "tipo_documento": self.partner_id.identification_type,
                "codigo_actividad": self.partner_id.fe_code_activity.code,
                "numero_documento": self._get_document_number(),
                "nombre": self.partner_id.name,
                "correo": self.partner_id.email
            }
            json_body["documento"]["renta_retenida"] = round(abs(self.amount_tax), 2)
            json_body["documento"]["sujeto_excluido"] = receptor_info
            # informacion de remitente
            self._get_address_error()
            direccion = {
                "departamento": str(self.partner_id.fe_address_dep.code),
                "municipio": str(self.partner_id.fe_address_mun.code_muni),
                "complemento": self.partner_id.complement_address,
            }
            # agrega al json la direccion y el correo
            json_body["documento"]["sujeto_excluido"]["direccion"] = direccion
        # IMPRIMIR JSON EN PANTALLA PARA VER ERRORES (COMENTAR PARA QUE FUNCIONE)
        # json_data = json.dumps(json_body)
        # raise ValidationError(str(json_data))
        if self.get_info_retension() > 0:
            json_body["documento"]["retener_iva"] = self.get_info_retension()
        self._get_address_error()
        direccion = {
            "departamento": str(self.partner_id.fe_address_dep.code or ''),
            "municipio": str(self.partner_id.fe_address_mun.code_muni),
            "complemento": self.partner_id.complement_address or '',
        }
        # receptor assignment
        if self.partner_id.nrc and self.partner_id.type_consumer_taxp == 'taxpayer':
            receptor_info.update({"nrc": self.partner_id.nrc})
        if self.partner_id.fe_code_activity.code:
            receptor_info.update({"codigo_actividad": self.partner_id.fe_code_activity.code})
        json_body["documento"]["receptor"] = receptor_info
        # agrega al json la direccion y el correo
        json_body["documento"]["receptor"]["direccion"] = direccion
        json_body["documento"]["receptor"]["correo"] = self.partner_id.email
        if self.partner_id.phone:
            json_body["documento"]["receptor"]["telefono"] = self.partner_id.phone
        json_body["documento"]["apendice"] = [{'campo': 'pedido_venta',
                                               'etiqueta': 'Pedido de venta asociado',
                                               'valor': self.invoice_origin or ''}]
        if self.invoice_user_id:
            json_body["documento"]["apendice"].append({'campo': 'vendedor',
                                                      'etiqueta': 'Vendedor',
                                                      'valor': self.invoice_user_id.name})

        if int(self.fe_type) == 14:
            json_body["documento"].pop('receptor')
        if len(json_body) != 0:
            if has_advance == True:
                json_body["documento"]["extension"] = {'nombre_entrega': self.env.user.partner_id.name,
                                                       'documento_entrega': self.env.user.partner_id.dui_field,
                                                       'observaciones': observations
                                                       }
            else:
                json_body["documento"]["extension"] = {'nombre_entrega': self.env.user.partner_id.name, 'documento_entrega': self.env.user.partner_id.dui_field}
            self.message_post(subject='FEL', body="Generando Factura Electronica FEL", attachments=[('Factura.json', str(json_body))])


            json_data = json.dumps(json_body)
            _logger.info("info FEL: " + str(json_data))
            self.prev_move_info = json_data
            urltest = self.company_id._get_fe_url()
            if not self.uuid_code:
                respuesta = requests.post(urltest, json_data, headers=headers)
                _logger.info(respuesta)
                como_json = respuesta.json()

                if como_json['ok'] == False:
                    # raise GeneracionResumenError(como_json['errores'])
                    raise UserError(str(como_json['errores']))
                else:
                    # datos de la factura
                    self.fact_info = como_json
                    self.uuid_code = como_json['respuesta']['codigoGeneracion']
                    self.date_certification = como_json['respuesta']['fechaEmision']
                    self.numero_control = como_json['respuesta']['numeroControl']
                    # guardar sello de recepcion
                    self.receipt_stamp = como_json['respuesta']['selloRecepcion']
                    # asignar pdf
                    self.fe_pdf = como_json['pdf_path']
        else:
            raise UserError("Tipo de DTE no disponible para esta version")

    def get_inf_items(self, numero_documento=None):
        result = []
        for item in self.invoice_line_ids:
            tributo_item = (item.price_total - item.price_subtotal)
            total_discount = (item.price_unit * item.quantity) - item.price_subtotal

            item_data = {
                "tipo": int(item.product_id.fe_services),
                "cantidad": item.quantity,
                "unidad_medida": int(item.product_id.fe_unidad_medida_id.code),
                "descuento": round(total_discount, 6) if total_discount > 0 else 0.0,
                "descripcion": item.name,
                "precio_unitario": round(item.price_unit, 6),
            }
            if self.fe_type == '05':
                item_data.update({'numero_documento': str(numero_documento)})
            if not len(item.tax_ids) > 0:
                item_data.update({'tipo_venta': '2'})
            if any('Exento IVA' in tax.name for tax in item.tax_ids):
                item_data.update({'tipo_venta': '3'})
            if any('IVA por Pagar' in tax.name for tax in item.tax_ids):
                tributos = []
                for tax in item.tax_ids:
                    if 'IVA por Pagar' in tax.name:
                        line_tribute = {'codigo': '20','monto':(item.price_unit * item.quantity) * (tax.amount/100 )}
                        tributos.append(line_tribute)
                item_data.update({'tributos': tributos})
            result.append(item_data)
        return result

    def get_info_retension(self):
        result = 0
        for line in self.invoice_line_ids:
            for l in line.tax_ids:
                if 'Gran Contribuyente' in l.name:
                    result += line.price_subtotal * (abs(l.amount)/100)
        return round(result, 2)

    def get_price_unit(self, line):
        if any('IVA por Pagar' in tax.name for tax in line.tax_ids):
            return round(line.price_unit * (1 + (line.tax_ids.filtered(lambda l: 'IVA por Pagar' in l.name).amount /100)), 5)
        else:
            return line.price_unit

    def extract_date(self, texto):
        # Patrón para fechas en formato DD/MM/YYYY
        patron = r"\b\d{2}/\d{2}/\d{4}\b"
        coincidencia = re.search(patron, texto)

        return coincidencia.group() if coincidencia else ""


class AccountMovePayment(models.Model):
    _name = 'account.move.payment'
    _description = 'Account Move Payment'
    _rec_name = 'move_id'
    _order = 'sequence,date'

    sequence = fields.Integer(string='Sequence')
    date = fields.Date(string='Date')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda s: s.env.company.currency_id)
    amount = fields.Monetary(string='Amount')
    move_id = fields.Many2one('account.move', string='Invoice')


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    fix_discount = fields.Float(string="Desc.(fix)")

