import requests
import json
import logging

from odoo import models, fields
from odoo.exceptions import UserError

TYPE_ASSETS = [
    ('01', 'Depósito'),
    ('02', 'Propiedad'),
    ('03', 'Consignación'),
    ('04', 'Traslado'),
    ('05', 'Otros'),
]

url_test = "https://certificador.infile.com.sv/api/v1/certificacion/test/documento/certificar"
url_prod = "https://certificador.infile.com.sv/api/v1/certificacion/prod/documento/certificar"

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = 'Stock Picking'

    fe_assets = fields.Selection(TYPE_ASSETS, string='Bienes Remitidos', store=True, help="Requerido si se desea crear una Nota de Remision", default="01")
    fe_nr_pdf = fields.Char(string='PDF')
    
    def get_nr_pdf(self):
        return {
            'type': 'ir.actions.act_url',
            'url': self.fe_nr_pdf,
            'download': True,
            'target': 'new',
        }
    
    def action_nr(self):
        if not self.fe_nr_pdf:
            items = []
            for line in self.move_ids_without_package:
                items.append({
                    "tipo": int(line.product_id.fe_services),
                    "cantidad": line.quantity,
                    "unidad_medida": int(line.product_id.fe_unidad_medida_id.code),
                    "descripcion": line.sale_line_id.name,
                    "precio_unitario": line.sale_line_id.price_unit,
                    "tributos": [{
                        "codigo": line.product_id.fe_tributes_id.code,
                        "monto": (line.quantity * line.sale_line_id.price_unit) * 0.13
                    }]
                })
            establishment = self.env.user.fe_establishment_id or self.company_id.fe_establishment_ids[0]
            document = {
                "documento": {
                    "tipo_dte": "04",
                    "establecimiento": establishment.fe_code,
                    "receptor": {
                        "tipo_documento": self.partner_id.identification_type,
                        "numero_documento": self.partner_id._get_document_number(),
                        "nombre": self.partner_id.name,
                        "nombre_comercial": self.partner_id.name,
                        "codigo_actividad": self.partner_id.fe_code_activity.code,
                        "direccion": {
                                "departamento": str(self.partner_id.fe_address_dep.code),
                                "municipio": str(self.partner_id.fe_address_mun.code_muni),
                                "complemento": self.partner_id.complement_address,
                        },
                        "correo": self.partner_id.email,
                        "titulo_bienes": self.fe_assets
                    },
                    "items": items
                }
            }
            if self.partner_id.type_consumer_taxp == "taxpayer":
                document["documento"]["receptor"].update({
                    "nrc": self.partner_id.nrc
                })
            headers = {
                "Content-Type": "application/json",
                "usuario": self.company_id.fe_user,
                "llave": self.company_id.fe_key_webservice
            }
            document = json.dumps(document)
            _logger.info(document)


            URL = url_prod if self.company_id.fe_mode_prod else url_test
            response = requests.post(URL, document, headers=headers)
            data = response.json()

            if not data['ok']:
                raise UserError(str(data['errores']))
            else:
                self.fe_nr_pdf = data['pdf_path']
                return self.get_nr_pdf()
        else:
            return self.get_nr_pdf()

