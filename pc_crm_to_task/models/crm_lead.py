# Copyright 2026 Process Control (https://www.processcontrol.es)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = "crm.lead"

    pc_task_ids = fields.One2many(
        comodel_name="project.task",
        inverse_name="pc_lead_id",
        string="Tasks created from this lead",
    )
    pc_task_count = fields.Integer(
        compute="_compute_pc_task_count",
        string="# tasks",
    )

    @api.depends("pc_task_ids")
    def _compute_pc_task_count(self):
        for lead in self:
            lead.pc_task_count = len(lead.pc_task_ids)

    # ------------------------------------------------------------------
    # Defaults resolution
    # ------------------------------------------------------------------
    def _pc_get_config(self, key, default=None):
        """Read a config_parameter from ir.config_parameter."""
        value = self.env["ir.config_parameter"].sudo().get_param(
            "pc_crm_to_task." + key, default
        )
        # Cast booleans coming back as strings
        if isinstance(default, bool):
            return str(value).lower() in ("1", "true", "yes", "t")
        return value

    def _pc_resolve_defaults(self):
        """Return effective defaults from stage > team > company hierarchy."""
        self.ensure_one()
        stage = self.stage_id
        team = self.team_id
        company = self.company_id or self.env.company

        project = (
            stage.pc_auto_task_project_id
            or team.pc_default_project_id
            or company.pc_default_project_id
        )
        task_stage = (
            team.pc_default_task_stage_id
            or company.pc_default_task_stage_id
        )
        strategy = self._pc_get_config("default_responsible_strategy", "team_default")
        if strategy == "lead_salesperson" and self.user_id:
            users = self.user_id
        elif strategy == "team_default":
            users = (
                team.pc_default_task_user_ids
                or company.pc_default_task_user_ids
                or self.env["res.users"]
            )
        elif strategy == "fixed_users":
            users = company.pc_default_task_user_ids
        else:  # "empty"
            users = self.env["res.users"]

        tags = (
            team.pc_default_task_tag_ids
            or company.pc_default_task_tag_ids
            or self.env["project.tags"]
        )
        mail_template = (
            team.pc_mail_template_id or company.pc_mail_template_id
        )
        return {
            "project_id": project,
            "stage_id": task_stage,
            "user_ids": users,
            "tag_ids": tags,
            "mail_template_id": mail_template,
            "activity_type_id": company.pc_activity_type_id,
        }

    # ------------------------------------------------------------------
    # Task creation
    # ------------------------------------------------------------------
    def _pc_prepare_task_vals(self, overrides=None):
        """Build vals dict for project.task creation."""
        self.ensure_one()
        defaults = self._pc_resolve_defaults()
        overrides = overrides or {}
        project = overrides.get("project_id") or defaults["project_id"]
        if not project:
            raise UserError(_(
                "No project defined for this lead. Configure a default project "
                "in Settings → CRM, on the CRM team, or pick one in the wizard."
            ))
        stage = overrides.get("stage_id") or defaults["stage_id"]
        users = overrides.get("user_ids", defaults["user_ids"])
        tags = overrides.get("tag_ids", defaults["tag_ids"])
        vals = {
            "name": overrides.get("name") or self.name,
            "description": overrides.get("description") or self.description,
            "project_id": project.id,
            "partner_id": (overrides.get("partner_id") or self.partner_id).id
            if (overrides.get("partner_id") or self.partner_id) else False,
            "date_deadline": overrides.get("date_deadline") or self.date_deadline,
            "priority": overrides.get("priority") or self.priority,
            "pc_lead_id": self.id,
        }
        if stage:
            vals["stage_id"] = stage.id
        if users:
            vals["user_ids"] = [(6, 0, users.ids)]
        if tags:
            vals["tag_ids"] = [(6, 0, tags.ids)]
        return vals

    def _pc_apply_transfers(self, task, overrides=None):
        """Move chatter/attachments/followers from lead to task per config."""
        self.ensure_one()
        overrides = overrides or {}

        transfer_messages = overrides.get(
            "transfer_messages",
            self._pc_get_config("transfer_messages", True),
        )
        transfer_attachments = overrides.get(
            "transfer_attachments",
            self._pc_get_config("transfer_attachments", True),
        )
        transfer_followers = overrides.get(
            "transfer_followers",
            self._pc_get_config("transfer_followers", False),
        )

        if transfer_messages:
            self.message_change_thread(task)
        if transfer_attachments:
            self.env["ir.attachment"].search([
                ("res_model", "=", "crm.lead"),
                ("res_id", "=", self.id),
            ]).write({"res_model": "project.task", "res_id": task.id})
        if transfer_followers:
            partner_ids = self.message_partner_ids.ids
            if partner_ids:
                task.message_subscribe(partner_ids=partner_ids)

    def _pc_send_notifications(self, task, overrides=None):
        """Send mail template + create activity per config and stage overrides."""
        self.ensure_one()
        overrides = overrides or {}
        stage = self.stage_id

        # Send mail
        send_mail = overrides.get(
            "send_mail",
            stage.pc_auto_task_send_mail
            if (overrides.get("from_auto") and stage)
            else self._pc_get_config("notification_send_mail", True),
        )
        if send_mail and task.user_ids:
            defaults = self._pc_resolve_defaults()
            template = overrides.get("mail_template_id") or defaults["mail_template_id"]
            if template:
                template.send_mail(task.id, force_send=False)

        # Create activity
        create_activity = overrides.get(
            "create_activity",
            stage.pc_auto_task_create_activity
            if (overrides.get("from_auto") and stage)
            else self._pc_get_config("notification_create_activity", True),
        )
        if create_activity and task.user_ids:
            defaults = self._pc_resolve_defaults()
            activity_type = (
                overrides.get("activity_type_id")
                or defaults["activity_type_id"]
                or self.env.ref(
                    "mail.mail_activity_data_todo", raise_if_not_found=False
                )
            )
            if activity_type:
                for user in task.user_ids:
                    task.activity_schedule(
                        activity_type_id=activity_type.id,
                        user_id=user.id,
                        summary=_("New task assigned from opportunity %s", self.name),
                    )

    def _pc_create_task(self, overrides=None):
        """Create the task, apply transfers, send notifications. Returns the task."""
        self.ensure_one()
        vals = self._pc_prepare_task_vals(overrides=overrides)
        task = self.env["project.task"].create(vals)
        self._pc_apply_transfers(task, overrides=overrides)
        self._pc_send_notifications(task, overrides=overrides)
        if self._pc_get_config("archive_lead_on_convert", False):
            self.active = False
        return task

    def _pc_open_task(self, task):
        """Return action that opens the task form."""
        return {
            "name": _("Task created"),
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "view_mode": "form",
            "res_id": task.id,
            "target": "current",
        }

    # ------------------------------------------------------------------
    # Entry-point actions
    # ------------------------------------------------------------------
    def action_pc_create_task(self):
        """Header button: decide between wizard or direct based on behavior_mode."""
        self.ensure_one()
        behavior = self._pc_get_config("behavior_mode", "wizard_if_missing")
        defaults = self._pc_resolve_defaults()
        has_project = bool(defaults["project_id"])
        has_users = bool(defaults["user_ids"])

        if behavior == "direct_if_defaults" and has_project and has_users:
            task = self._pc_create_task()
            return self._pc_open_task(task)
        if behavior == "wizard_if_missing" and has_project and has_users:
            task = self._pc_create_task()
            return self._pc_open_task(task)
        # Otherwise open wizard
        return {
            "name": _("Create task from lead"),
            "type": "ir.actions.act_window",
            "res_model": "crm.lead.to.task.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_lead_id": self.id},
        }

    def action_pc_view_tasks(self):
        """Smart button: list tasks linked to this lead."""
        self.ensure_one()
        return {
            "name": _("Tasks from %s", self.name),
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "view_mode": "list,form",
            "domain": [("pc_lead_id", "=", self.id)],
            "context": {"default_pc_lead_id": self.id},
        }

    # ------------------------------------------------------------------
    # Auto-create on stage change
    # ------------------------------------------------------------------
    def write(self, vals):
        res = super().write(vals)
        if "stage_id" not in vals:
            return res
        if self.env.context.get("pc_skip_auto_task_creation"):
            return res
        if not self._pc_get_config("enable_auto_creation_on_stage", True):
            return res
        skip_if_has_task = self._pc_get_config(
            "auto_creation_skip_if_lead_has_task", True
        )
        for lead in self:
            stage = lead.stage_id
            if not stage or not stage.pc_auto_create_task:
                continue
            if skip_if_has_task and lead.pc_task_ids:
                continue
            lead.with_context(pc_skip_auto_task_creation=True)._pc_create_task(
                overrides={"from_auto": True}
            )
        return res
