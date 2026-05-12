# Copyright 2026 Process Control (https://www.processcontrol.es)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    # Defaults for task creation from CRM (level: company)
    pc_default_project_id = fields.Many2one(
        comodel_name="project.project",
        string="Default project for CRM → Task",
        help="Default project used when creating a task from a CRM lead. "
             "Can be overridden at CRM team or CRM stage level.",
    )
    pc_default_task_stage_id = fields.Many2one(
        comodel_name="project.task.type",
        string="Default task stage for CRM → Task",
        domain="[('project_ids', 'in', pc_default_project_id)]",
    )
    pc_default_task_user_ids = fields.Many2many(
        comodel_name="res.users",
        relation="pc_company_default_task_user_rel",
        column1="company_id",
        column2="user_id",
        string="Default assignees for CRM → Task",
    )
    pc_default_task_tag_ids = fields.Many2many(
        comodel_name="project.tags",
        relation="pc_company_default_task_tag_rel",
        column1="company_id",
        column2="tag_id",
        string="Default tags for CRM → Task",
    )

    # Notification settings
    pc_mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Notification mail template",
        domain="[('model', '=', 'project.task')]",
        default=lambda self: self.env.ref(
            "pc_crm_to_task.mail_template_task_from_lead",
            raise_if_not_found=False,
        ),
    )
    pc_activity_type_id = fields.Many2one(
        comodel_name="mail.activity.type",
        string="Activity type for task notification",
        default=lambda self: self.env.ref(
            "pc_crm_to_task.mail_activity_data_task_from_lead",
            raise_if_not_found=False,
        ),
    )
