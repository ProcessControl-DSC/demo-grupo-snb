# Copyright 2026 Process Control (https://www.processcontrol.es)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
"""
post-translations migration script for pc_crm_to_task 19.0.1.0.4.

Why this exists
---------------
When a view's <setting string="..."> term is **renamed** between two versions
of the module, Odoo keeps the *original* en_US source recorded in the JSONB
``arch_db`` field (``_en_US`` key). The TranslationImporter only re-applies
translations whose msgid matches that recorded source. Renamed terms lose
the match and the new translations from the ``.po`` are silently ignored —
even when ``_update_translations`` is called with ``overwrite=True``.

This script forces a clean reload of translations for the module:
1. Drops the ``es_ES`` key from ``arch_db`` of every view owned by the module.
2. Calls ``_update_translations(['es_ES'], overwrite=True)`` so the
   importer reads the ``.po`` and re-populates the JSONB from scratch.

It is harmless if there's nothing to retranslate.
"""
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # cr is the raw cursor; we need an env to operate cleanly
    from odoo.api import Environment
    from odoo import SUPERUSER_ID
    env = Environment(cr, SUPERUSER_ID, {})

    module = env["ir.module.module"].search([("name", "=", "pc_crm_to_task")])
    if not module:
        return

    # Find every view owned by the module
    view_ids = env["ir.model.data"].search([
        ("module", "=", "pc_crm_to_task"),
        ("model", "=", "ir.ui.view"),
    ]).mapped("res_id")

    if view_ids:
        # Drop the es_ES key from each view so the importer rebuilds it
        cr.execute(
            "UPDATE ir_ui_view SET arch_db = arch_db - 'es_ES' "
            "WHERE id = ANY(%s)",
            (view_ids,),
        )
        _logger.info(
            "pc_crm_to_task: dropped es_ES translation from %s views",
            len(view_ids),
        )

    # Force-reload translations from the .po
    try:
        module._update_translations(["es_ES"], overwrite=True)
        _logger.info("pc_crm_to_task: translations reloaded for es_ES")
    except Exception as exc:  # pragma: no cover
        _logger.warning(
            "pc_crm_to_task: translation reload failed: %s", exc
        )
