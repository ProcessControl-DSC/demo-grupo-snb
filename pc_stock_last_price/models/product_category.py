# Copyright 2026 Process Control (https://www.processcontrol.es)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    last_price_update_enabled = fields.Boolean(
        string="Use last purchase price",
        help=(
            "When enabled, the standard price of products in this category is "
            "automatically updated with the unit price of every received "
            "purchase. Works on top of the regular costing method."
        ),
    )
