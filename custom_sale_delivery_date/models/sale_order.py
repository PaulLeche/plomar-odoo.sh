from odoo import models, fields, api
from datetime import timedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    # date_action = fields.Datetime('Date current action', required=False, readonly=False)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        date_action = fields.Datetime.now()
        delivery_date = date_action + timedelta(days=5)

        self.write({
            'commitment_date': delivery_date
        })

        return res
