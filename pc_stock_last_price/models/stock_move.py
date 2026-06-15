# Copyright 2026 Process Control (https://www.processcontrol.es)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        self._pc_update_standard_price_from_last_receipt()
        return res

    def _pc_update_standard_price_from_last_receipt(self):
        for move in self:
            picking = move.picking_id
            if not picking or picking.picking_type_id.code != "incoming":
                continue
            product = move.product_id
            if not product or not product.categ_id.last_price_update_enabled:
                continue
            price = move.price_unit
            if not price or price <= 0:
                continue
            product.with_company(move.company_id).sudo().write(
                {"standard_price": price}
            )
            _logger.info(
                "pc_stock_last_price: %s standard_price -> %s (picking %s)",
                product.display_name,
                price,
                picking.name,
            )
