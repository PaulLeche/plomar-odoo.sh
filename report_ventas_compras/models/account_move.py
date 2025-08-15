# -*- encoding: UTF-8 -*-

from odoo import fields, models, api, _
import logging

_logger = logging.getLogger( __name__ )


class AccountMoveLine(models.Model):
	_inherit = "account.move.line"

	tipo_gasto = fields.Selection(string="Tipo Gasto", store=True, default='compra', selection='_get_tipo_gasto', required=True, help="Tipo de gasto que se reflejara en el libro de Ventas/Compras del IVA")

	def _get_tipo_gasto(self):
		if self._context.get('default_move_type') and self._context.get('default_move_type') == 'out_invoice':
			selection = [
				('compra', 'Bienes'), 
				('servicio', 'Servicios'),
				('n/a', 'N/A')
			]
		else: 
			selection = [
				('combustibles', 'Combustibles/Lubricantes'),
				('compra', 'Bienes'), 
				('servicio', 'Servicios'), 
				('importacion', 'Importaciones'), 
				('peqcontribuyente', 'Pequeño Contribuyente'), 
				('n/a', 'N/A')
			]
		return selection  
        
	@api.onchange('product_id')
	def _onchange_expense_type(self):
		for order in self:
			if order.product_id:
				order.tipo_gasto = order.product_id.tipo_gasto if order.product_id.tipo_gasto else ""
