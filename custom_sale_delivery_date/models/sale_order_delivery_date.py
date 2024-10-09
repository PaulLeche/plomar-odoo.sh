import logging
from odoo import _, models, fields, api
from datetime import timedelta, datetime, date
_logger = logging.getLogger(__name__)

class SaleOrderDeliveryDate(models.Model):
    _inherit = 'sale.order'
    # date_action = fields.Datetime('Date current action', required=False, readonly=False)

    def action_confirm(self):
        res = super(SaleOrderDeliveryDate, self).action_confirm()
        date_action = fields.Datetime.now()
        delivery_date = date_action + timedelta(days=5)
        print(f"Custom delivery date 1: {delivery_date}")
        print(f"Custom delivery date 2: {delivery_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        self.write({
            'commitment_date': delivery_date.strftime('%Y-%m-%d %H:%M:%S')
        })

        return res
