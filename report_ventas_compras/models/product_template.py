# -*- encoding: UTF-8 -*-

from odoo import fields, models, api, _

class ProductTemplate(models.Model):
	_inherit = "product.template"
	
	tipo_gasto = fields.Selection([
            ('compra', 'Bienes'), 
            ('servicio', 'Servicios'), 
            ('combustibles', 'Combustibles/Lubricantes'), 
            ('importacion', 'Importaciones'), 
            ('exportacion', 'Exportaciones'), 
            ('peqcontribuyente', 'Pequeño Contribuyente'), 
            ('n/a', 'N/A')
		], 
		string='Tipo Gasto', 
		default='compra', 
		required=True, 
		help="Tipo de gasto que se reflejara en el libro de Ventas/Compras del IVA"
	)
	