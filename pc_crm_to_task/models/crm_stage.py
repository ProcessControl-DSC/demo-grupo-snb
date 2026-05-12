# Copyright 2026 Process Control (https://www.processcontrol.es)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class CrmStage(models.Model):
    _inherit = "crm.stage"

    pc_auto_create_task = fields.Boolean(
        string="Auto-create task on entry",
        help="When a lead is moved to this stage, automatically create "
             "a task using the resolved defaults (stage > team > company).",
    )
    pc_auto_task_project_id = fields.Many2one(
        comodel_name="project.project",
        string="Forced project for auto-creation",
        help="If set, this project wins over team/company defaults "
             "when auto-creating from this stage.",
    )
    pc_auto_task_send_mail = fields.Boolean(
        string="Send mail on auto-create",
        default=True,
    )
    pc_auto_task_create_activity = fields.Boolean(
        string="Create activity on auto-create",
        default=True,
    )
