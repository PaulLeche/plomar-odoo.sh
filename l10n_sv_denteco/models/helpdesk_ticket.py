# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re
from odoo.exceptions import UserError

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    # Relación con el ticket de soporte
    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket de Soporte')

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Relación con el ticket de soporte
    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket de Soporte')


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    # Relación con las reuniones (calendario)
    meeting_ids = fields.One2many('calendar.event', 'helpdesk_ticket_id', string='Reuniones')

    # Relación con el presupuesto (sales order)
    sale_order_id = fields.Many2one('sale.order', string='Presupuesto', domain="[('state', 'in', ['draft', 'sent'])]")


    # Función para abrir la vista de reuniones asociadas
    def action_schedule_meeting(self):
        self.ensure_one()
        
        # Obtiene la acción para abrir el calendario
        action = self.env["ir.actions.actions"]._for_xml_id("calendar.action_calendar_event")  # Acción de calendario
        
        # Configura el contexto con el ID del ticket actual
        action['context'] = {
            'default_helpdesk_ticket_id': self.id,  # Pasa el ticket de Helpdesk al contexto de la reunión
            'default_partner_ids': [(6, 0, [self.partner_id.id, self.env.user.partner_id.id])],  # Relaciona el cliente con la reunión
            'default_user_id': self.env.user.id,
            'default_name': self.name,
        }
        
        # Filtra las reuniones por el ticket actual
        action['domain'] = [('helpdesk_ticket_id', '=', self.id)]  
        
        return action

        # Función para crear un presupuesto (orden de venta)
    def action_create_sale_order(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'view_id': self.env.ref('sale.view_order_form').id,  # Vista de presupuesto
            'target': 'current',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_origin': self.name,
                'default_helpdesk_ticket_id': self.id,
            }
        }

    # Función para abrir el presupuesto existente
    def action_open_sale_order(self):
        self.ensure_one()

        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")  # Acción de Pedidos de Venta

        # Filtrar los pedidos de venta relacionados con este ticket
        action['domain'] = [('helpdesk_ticket_id', '=', self.id)]

        return action


