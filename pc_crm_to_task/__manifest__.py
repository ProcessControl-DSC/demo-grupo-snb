# Copyright 2026 Process Control (https://www.processcontrol.es)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "PC CRM to Task",
    "summary": "Create project tasks from CRM leads/opportunities with multi-level defaults",
    "version": "19.0.1.0.3",
    "category": "Sales/CRM",
    "author": "Process Control",
    "website": "https://www.processcontrol.es",
    "license": "LGPL-3",
    "depends": [
        "crm",
        "project",
        "mail",
    ],
    "post_init_hook": "post_init_hook",
    "data": [
        "security/ir.model.access.csv",
        "data/mail_activity_data.xml",
        "data/mail_template_data.xml",
        "wizard/crm_to_task_wizard_views.xml",
        "views/crm_lead_views.xml",
        "views/crm_stage_views.xml",
        "views/crm_team_views.xml",
        "views/project_task_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
