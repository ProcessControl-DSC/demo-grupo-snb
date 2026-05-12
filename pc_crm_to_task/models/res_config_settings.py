# Copyright 2026 Process Control (https://www.processcontrol.es)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Behavior
    pc_crm_to_task_behavior_mode = fields.Selection(
        selection=[
            ("always_wizard", "Always open wizard"),
            ("wizard_if_missing", "Open wizard only when defaults are incomplete"),
            ("direct_if_defaults", "Create directly if defaults are complete"),
        ],
        string="CRM → Task behavior",
        default="wizard_if_missing",
        config_parameter="pc_crm_to_task.behavior_mode",
    )
    pc_crm_to_task_responsible_strategy = fields.Selection(
        selection=[
            ("lead_salesperson", "Use lead salesperson"),
            ("team_default", "Use CRM team default (fallback company)"),
            ("fixed_users", "Use company default users"),
            ("empty", "Leave empty"),
        ],
        string="Default responsible strategy",
        default="team_default",
        config_parameter="pc_crm_to_task.default_responsible_strategy",
    )

    # Transfers
    pc_crm_to_task_transfer_messages = fields.Boolean(
        string="Move lead chatter to task",
        default=True,
        config_parameter="pc_crm_to_task.transfer_messages",
    )
    pc_crm_to_task_transfer_attachments = fields.Boolean(
        string="Move lead attachments to task",
        default=True,
        config_parameter="pc_crm_to_task.transfer_attachments",
    )
    pc_crm_to_task_transfer_followers = fields.Boolean(
        string="Copy lead followers to task",
        default=False,
        config_parameter="pc_crm_to_task.transfer_followers",
    )
    pc_crm_to_task_archive_lead = fields.Boolean(
        string="Archive lead on convert",
        default=False,
        config_parameter="pc_crm_to_task.archive_lead_on_convert",
    )
    pc_crm_to_task_link_back = fields.Boolean(
        string="Show 'Opportunity' smart button on task",
        default=True,
        config_parameter="pc_crm_to_task.link_back_to_lead",
    )

    # Auto creation on stage change
    pc_crm_to_task_enable_auto_on_stage = fields.Boolean(
        string="Enable auto-create task on CRM stage change",
        default=True,
        config_parameter="pc_crm_to_task.enable_auto_creation_on_stage",
    )
    pc_crm_to_task_skip_if_lead_has_task = fields.Boolean(
        string="Skip auto-create if lead already has a task",
        default=True,
        config_parameter="pc_crm_to_task.auto_creation_skip_if_lead_has_task",
    )

    # Notifications
    pc_crm_to_task_send_mail = fields.Boolean(
        string="Send notification mail to assignees",
        default=True,
        config_parameter="pc_crm_to_task.notification_send_mail",
    )
    pc_crm_to_task_create_activity = fields.Boolean(
        string="Create activity on task for assignees",
        default=True,
        config_parameter="pc_crm_to_task.notification_create_activity",
    )

    # Company defaults (exposed)
    pc_default_project_id = fields.Many2one(
        related="company_id.pc_default_project_id",
        readonly=False,
    )
    pc_default_task_stage_id = fields.Many2one(
        related="company_id.pc_default_task_stage_id",
        readonly=False,
    )
    pc_default_task_user_ids = fields.Many2many(
        related="company_id.pc_default_task_user_ids",
        readonly=False,
    )
    pc_default_task_tag_ids = fields.Many2many(
        related="company_id.pc_default_task_tag_ids",
        readonly=False,
    )
    pc_mail_template_id = fields.Many2one(
        related="company_id.pc_mail_template_id",
        readonly=False,
    )
    pc_activity_type_id = fields.Many2one(
        related="company_id.pc_activity_type_id",
        readonly=False,
    )
