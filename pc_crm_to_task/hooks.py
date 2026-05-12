# Copyright 2026 Process Control (https://www.processcontrol.es)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Backfill defaults on companies that pre-existed before this module
    was installed.

    The ``default=lambda...`` on ``res.company.pc_mail_template_id`` and
    ``res.company.pc_activity_type_id`` only fires when *new* companies are
    created. Existing companies installed prior to this module keep the
    fields empty, so we set them here once.
    """
    template = env.ref(
        "pc_crm_to_task.mail_template_task_from_lead",
        raise_if_not_found=False,
    )
    activity = env.ref(
        "pc_crm_to_task.mail_activity_data_task_from_lead",
        raise_if_not_found=False,
    )
    if not template and not activity:
        _logger.info(
            "pc_crm_to_task: no template/activity reference found, "
            "skipping post_init backfill"
        )
        return

    companies = env["res.company"].search([])
    updated = 0
    for company in companies:
        vals = {}
        if template and not company.pc_mail_template_id:
            vals["pc_mail_template_id"] = template.id
        if activity and not company.pc_activity_type_id:
            vals["pc_activity_type_id"] = activity.id
        if vals:
            company.write(vals)
            updated += 1
    _logger.info(
        "pc_crm_to_task: backfilled defaults on %s companies", updated
    )
