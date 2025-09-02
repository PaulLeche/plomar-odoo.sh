# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, SUPERUSER_ID, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    def action_nr(self):
        return True

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    type_of_sale = fields.Selection([('1', 'Ventas exentas'),
                                     ('2', 'Ventas internas Exentas No Sujetas a Proporcionalidad'),
                                     ('3', 'Ventas no sujeta'),
                                     ('4', 'Ventas gravadas locales'),
                                     ('5', 'Exportaciones dentro del área centroamericana'),
                                     ('6', 'Exportaciones fuera del área centroamericana'),
                                     ('7', 'Exportaciones de servicios'),
                                     ('8', 'Ventas a zonas Francas y DPA (Tasa cero)'),
                                     ('9', 'Ventas a cuentas de terceros no domiciliados'),
                                     ('10', 'Ventas a cuentas de terceros domiciliados')],
                                     string='Tipo de venta')