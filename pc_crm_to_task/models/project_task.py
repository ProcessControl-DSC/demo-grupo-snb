# Copyright 2026 Process Control (https://www.processcontrol.es)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import _, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    pc_lead_id = fields.Many2one(
        comodel_name="crm.lead",
        string="Originating opportunity",
        index=True,
        ondelete="set null",
        help="CRM lead/opportunity this task was created from.",
    )

    def action_pc_view_lead(self):
        """Smart button: open the originating lead."""
        self.ensure_one()
        if not self.pc_lead_id:
            return False
        return {
            "name": _("Opportunity"),
            "type": "ir.actions.act_window",
            "res_model": "crm.lead",
            "view_mode": "form",
            "res_id": self.pc_lead_id.id,
            "target": "current",
        }
