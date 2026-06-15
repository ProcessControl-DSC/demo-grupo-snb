# Copyright 2026 Process Control (https://www.processcontrol.es)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "PC Stock Last Purchase Price",
    "summary": "Update product standard price with the last received purchase price",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "author": "Process Control",
    "website": "https://www.processcontrol.es",
    "license": "LGPL-3",
    "depends": [
        "stock",
        "purchase_stock",
    ],
    "data": [
        "views/product_category_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
