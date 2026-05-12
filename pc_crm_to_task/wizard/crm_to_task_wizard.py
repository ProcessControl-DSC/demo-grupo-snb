# Copyright 2026 Process Control (https://www.processcontrol.es)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CrmLeadToTaskWizard(models.TransientModel):
    _name = "crm.lead.to.task.wizard"
    _description = "Wizard to create a project task from a CRM lead"

    lead_id = fields.Many2one(
        comodel_name="crm.lead",
        string="Lead",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(string="Task name", required=True)
    description = fields.Html(string="Description")
    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        required=True,
    )
    stage_id = fields.Many2one(
        comodel_name="project.task.type",
        string="Stage",
        domain="[('project_ids', 'in', project_id)]",
    )
    user_ids = fields.Many2many(
        comodel_name="res.users",
        relation="pc_wizard_crm_to_task_user_rel",
        column1="wizard_id",
        column2="user_id",
        string="Assignees",
    )
    tag_ids = fields.Many2many(
        comodel_name="project.tags",
        relation="pc_wizard_crm_to_task_tag_rel",
        column1="wizard_id",
        column2="tag_id",
        string="Tags",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
    )
    date_deadline = fields.Datetime(string="Deadline")
    priority = fields.Selection(
        selection=[("0", "Normal"), ("1", "Important")],
        string="Priority",
        default="0",
    )

    # Per-execution overrides
    transfer_messages = fields.Boolean(
        string="Move lead chatter to task", default=True,
    )
    transfer_attachments = fields.Boolean(
        string="Move lead attachments to task", default=True,
    )
    transfer_followers = fields.Boolean(
        string="Copy lead followers to task", default=False,
    )
    send_mail = fields.Boolean(
        string="Send notification mail", default=True,
    )
    create_activity = fields.Boolean(
        string="Create activity for assignees", default=True,
    )
    archive_lead = fields.Boolean(string="Archive lead on convert")

    @api.model
    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        lead_id = result.get("lead_id") or self.env.context.get("default_lead_id")
        if not lead_id:
            return result
        lead = self.env["crm.lead"].browse(lead_id)
        defaults = lead._pc_resolve_defaults()
        icp = self.env["ir.config_parameter"].sudo()

        def _flag(key, default):
            return str(
                icp.get_param("pc_crm_to_task." + key, default)
            ).lower() in ("1", "true", "yes", "t")

        result.update({
            "lead_id": lead.id,
            "name": lead.name,
            "description": lead.description,
            "project_id": defaults["project_id"].id if defaults["project_id"] else False,
            "stage_id": defaults["stage_id"].id if defaults["stage_id"] else False,
            "user_ids": [(6, 0, defaults["user_ids"].ids)],
            "tag_ids": [(6, 0, defaults["tag_ids"].ids)],
            "partner_id": lead.partner_id.id if lead.partner_id else False,
            "date_deadline": lead.date_deadline,
            "priority": lead.priority or "0",
            "transfer_messages": _flag("transfer_messages", True),
            "transfer_attachments": _flag("transfer_attachments", True),
            "transfer_followers": _flag("transfer_followers", False),
            "send_mail": _flag("notification_send_mail", True),
            "create_activity": _flag("notification_create_activity", True),
            "archive_lead": _flag("archive_lead_on_convert", False),
        })
        return result

    def action_create_task(self):
        self.ensure_one()
        if not self.lead_id:
            raise UserError(_("No lead linked to the wizard."))
        overrides = {
            "name": self.name,
            "description": self.description,
            "project_id": self.project_id,
            "stage_id": self.stage_id,
            "user_ids": self.user_ids,
            "tag_ids": self.tag_ids,
            "partner_id": self.partner_id,
            "date_deadline": self.date_deadline,
            "priority": self.priority,
            "transfer_messages": self.transfer_messages,
            "transfer_attachments": self.transfer_attachments,
            "transfer_followers": self.transfer_followers,
            "send_mail": self.send_mail,
            "create_activity": self.create_activity,
        }
        task = self.lead_id._pc_create_task(overrides=overrides)
        if self.archive_lead:
            self.lead_id.active = False
        return self.lead_id._pc_open_task(task)
