# Copyright 2026 Process Control (https://www.processcontrol.es)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    pc_default_project_id = fields.Many2one(
        comodel_name="project.project",
        string="Default project for CRM → Task",
        help="Overrides the company default when creating a task "
             "from a lead assigned to this team.",
    )
    pc_default_task_stage_id = fields.Many2one(
        comodel_name="project.task.type",
        string="Default task stage",
        domain="[('project_ids', 'in', pc_default_project_id)]",
    )
    pc_default_task_user_ids = fields.Many2many(
        comodel_name="res.users",
        relation="pc_team_default_task_user_rel",
        column1="team_id",
        column2="user_id",
        string="Default assignees",
    )
    pc_default_task_tag_ids = fields.Many2many(
        comodel_name="project.tags",
        relation="pc_team_default_task_tag_rel",
        column1="team_id",
        column2="tag_id",
        string="Default tags",
    )
    pc_mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Notification mail template (override)",
        domain="[('model', '=', 'project.task')]",
    )
