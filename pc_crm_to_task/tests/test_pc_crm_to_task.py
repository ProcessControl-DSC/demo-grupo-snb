# Copyright 2026 Process Control (https://www.processcontrol.es)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPcCrmToTask(TransactionCase):
    """Tests for pc_crm_to_task module."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))

        cls.company = cls.env.company
        cls.partner = cls.env["res.partner"].create({"name": "Demo customer"})
        cls.user_a = cls.env["res.users"].create({
            "name": "User A",
            "login": "user_a_pc_crm_to_task@example.com",
        })
        cls.user_b = cls.env["res.users"].create({
            "name": "User B",
            "login": "user_b_pc_crm_to_task@example.com",
        })

        cls.project_main = cls.env["project.project"].create({
            "name": "Main project",
        })
        cls.project_alt = cls.env["project.project"].create({
            "name": "Alt project",
        })
        cls.project_stage = cls.env["project.project"].create({
            "name": "Stage-forced project",
        })

        cls.team = cls.env["crm.team"].create({"name": "Team Pc Test"})
        cls.stage_new = cls.env["crm.stage"].create({
            "name": "PcTest New",
            "sequence": 1,
        })
        cls.stage_won = cls.env["crm.stage"].create({
            "name": "PcTest Won",
            "sequence": 99,
            "is_won": True,
        })

        cls.icp = cls.env["ir.config_parameter"].sudo()
        # Defaults sane for tests
        cls.icp.set_param("pc_crm_to_task.behavior_mode", "wizard_if_missing")
        cls.icp.set_param("pc_crm_to_task.default_responsible_strategy", "team_default")
        cls.icp.set_param("pc_crm_to_task.transfer_messages", "True")
        cls.icp.set_param("pc_crm_to_task.transfer_attachments", "True")
        cls.icp.set_param("pc_crm_to_task.transfer_followers", "False")
        cls.icp.set_param("pc_crm_to_task.archive_lead_on_convert", "False")
        cls.icp.set_param("pc_crm_to_task.enable_auto_creation_on_stage", "True")
        cls.icp.set_param("pc_crm_to_task.auto_creation_skip_if_lead_has_task", "True")
        cls.icp.set_param("pc_crm_to_task.notification_send_mail", "False")
        cls.icp.set_param("pc_crm_to_task.notification_create_activity", "False")

    def _make_lead(self, **kw):
        vals = {
            "name": kw.get("name", "Demo opportunity"),
            "type": "opportunity",
            "partner_id": kw.get("partner_id", self.partner.id),
            "team_id": kw.get("team_id", self.team.id),
            "stage_id": kw.get("stage_id", self.stage_new.id),
            "description": kw.get("description", "<p>Description body</p>"),
        }
        return self.env["crm.lead"].create(vals)

    # ------------------------------------------------------------------
    # 1. Basic creation
    # ------------------------------------------------------------------
    def test_01_basic_create_task_links_lead(self):
        """Direct task creation links task.pc_lead_id back to the lead."""
        self.company.pc_default_project_id = self.project_main
        lead = self._make_lead()
        task = lead._pc_create_task()
        self.assertEqual(task.pc_lead_id, lead)
        self.assertEqual(task.project_id, self.project_main)
        self.assertEqual(task.name, lead.name)

    # ------------------------------------------------------------------
    # 2-4. Hierarchy resolution
    # ------------------------------------------------------------------
    def test_02_company_default_applied_when_no_team(self):
        """Company project default applies when team has no override."""
        self.company.pc_default_project_id = self.project_main
        lead = self._make_lead(team_id=False)
        defaults = lead._pc_resolve_defaults()
        self.assertEqual(defaults["project_id"], self.project_main)

    def test_03_team_default_overrides_company(self):
        """CRM team default wins over company default."""
        self.company.pc_default_project_id = self.project_main
        self.team.pc_default_project_id = self.project_alt
        lead = self._make_lead()
        defaults = lead._pc_resolve_defaults()
        self.assertEqual(defaults["project_id"], self.project_alt)

    def test_04_stage_forced_project_wins(self):
        """Stage pc_auto_task_project_id wins over team and company."""
        self.company.pc_default_project_id = self.project_main
        self.team.pc_default_project_id = self.project_alt
        self.stage_won.pc_auto_task_project_id = self.project_stage
        lead = self._make_lead(stage_id=self.stage_won.id)
        defaults = lead._pc_resolve_defaults()
        self.assertEqual(defaults["project_id"], self.project_stage)

    # ------------------------------------------------------------------
    # 5. Wizard overrides
    # ------------------------------------------------------------------
    def test_05_wizard_overrides_defaults(self):
        """Wizard's project_id wins over all resolved defaults."""
        self.company.pc_default_project_id = self.project_main
        self.team.pc_default_project_id = self.project_alt
        lead = self._make_lead()
        wizard = self.env["crm.lead.to.task.wizard"].with_context(
            default_lead_id=lead.id
        ).create({
            "lead_id": lead.id,
            "name": "Custom task",
            "project_id": self.project_stage.id,
        })
        wizard.action_create_task()
        task = lead.pc_task_ids
        self.assertEqual(len(task), 1)
        self.assertEqual(task.project_id, self.project_stage)
        self.assertEqual(task.name, "Custom task")

    # ------------------------------------------------------------------
    # 6-7. Behavior mode
    # ------------------------------------------------------------------
    def test_06_behavior_direct_creates_task_when_defaults_complete(self):
        """direct_if_defaults: button creates task immediately when defaults ok."""
        self.icp.set_param("pc_crm_to_task.behavior_mode", "direct_if_defaults")
        self.company.pc_default_project_id = self.project_main
        self.company.pc_default_task_user_ids = self.user_a
        lead = self._make_lead()
        action = lead.action_pc_create_task()
        self.assertEqual(action.get("res_model"), "project.task")
        self.assertEqual(len(lead.pc_task_ids), 1)

    def test_07_behavior_always_wizard_returns_wizard_action(self):
        """always_wizard: button returns wizard action regardless of defaults."""
        self.icp.set_param("pc_crm_to_task.behavior_mode", "always_wizard")
        self.company.pc_default_project_id = self.project_main
        self.company.pc_default_task_user_ids = self.user_a
        lead = self._make_lead()
        action = lead.action_pc_create_task()
        self.assertEqual(action.get("res_model"), "crm.lead.to.task.wizard")
        self.assertFalse(lead.pc_task_ids)

    # ------------------------------------------------------------------
    # 8-9. Transfers
    # ------------------------------------------------------------------
    def test_08_transfer_attachments_moves_files_to_task(self):
        """Attachments on the lead are moved to the new task when enabled."""
        self.company.pc_default_project_id = self.project_main
        lead = self._make_lead()
        att = self.env["ir.attachment"].create({
            "name": "demo.txt",
            "res_model": "crm.lead",
            "res_id": lead.id,
            "raw": b"hello",
        })
        task = lead._pc_create_task(overrides={"transfer_attachments": True})
        att.invalidate_model()
        self.assertEqual(att.res_model, "project.task")
        self.assertEqual(att.res_id, task.id)

    def test_09_transfer_attachments_disabled_keeps_files_on_lead(self):
        """When transfer_attachments=False the attachment stays on the lead."""
        self.company.pc_default_project_id = self.project_main
        lead = self._make_lead()
        att = self.env["ir.attachment"].create({
            "name": "demo.txt",
            "res_model": "crm.lead",
            "res_id": lead.id,
            "raw": b"hello",
        })
        lead._pc_create_task(overrides={"transfer_attachments": False})
        att.invalidate_model()
        self.assertEqual(att.res_model, "crm.lead")
        self.assertEqual(att.res_id, lead.id)

    # ------------------------------------------------------------------
    # 10. Archive lead
    # ------------------------------------------------------------------
    def test_10_archive_lead_on_convert(self):
        """archive_lead_on_convert deactivates the lead after creation."""
        self.icp.set_param("pc_crm_to_task.archive_lead_on_convert", "True")
        self.company.pc_default_project_id = self.project_main
        lead = self._make_lead()
        lead._pc_create_task()
        self.assertFalse(lead.active)

    # ------------------------------------------------------------------
    # 11-13. Auto creation on stage change
    # ------------------------------------------------------------------
    def test_11_auto_create_on_stage_change(self):
        """Moving a lead to a stage with pc_auto_create_task creates a task."""
        self.stage_won.pc_auto_create_task = True
        self.stage_won.pc_auto_task_project_id = self.project_stage
        lead = self._make_lead()
        self.assertFalse(lead.pc_task_ids)
        lead.stage_id = self.stage_won
        self.assertEqual(len(lead.pc_task_ids), 1)
        self.assertEqual(lead.pc_task_ids.project_id, self.project_stage)

    def test_12_kill_switch_disables_auto_creation(self):
        """Global kill switch off prevents auto-create even if stage is configured."""
        self.icp.set_param("pc_crm_to_task.enable_auto_creation_on_stage", "False")
        self.stage_won.pc_auto_create_task = True
        self.stage_won.pc_auto_task_project_id = self.project_stage
        lead = self._make_lead()
        lead.stage_id = self.stage_won
        self.assertFalse(lead.pc_task_ids)

    def test_13_skip_auto_when_lead_already_has_task(self):
        """If lead has a task and skip flag is on, no duplicate is created."""
        self.company.pc_default_project_id = self.project_main
        self.stage_won.pc_auto_create_task = True
        self.stage_won.pc_auto_task_project_id = self.project_stage
        lead = self._make_lead()
        lead._pc_create_task()  # one task already exists
        self.assertEqual(len(lead.pc_task_ids), 1)
        lead.stage_id = self.stage_won  # would normally trigger auto
        self.assertEqual(len(lead.pc_task_ids), 1)

    # ------------------------------------------------------------------
    # 14. Smart button count
    # ------------------------------------------------------------------
    def test_14_smart_button_counts_tasks(self):
        """pc_task_count reflects the number of tasks created from the lead."""
        self.company.pc_default_project_id = self.project_main
        lead = self._make_lead()
        lead._pc_create_task()
        lead._pc_create_task()
        self.assertEqual(lead.pc_task_count, 2)
