# Copyright (c) 2026, FEDCO
# License: MIT

app_name = "fedco_ess"
app_title = "FEDCO ESS"
app_publisher = "FEDCO"
app_description = "Employee Self-Service portal for ERPNext: a branded hub over Frappe HR"
app_email = "it@fedco.example"
app_license = "mit"
app_version = "1.0.0"

# Frappe HR supplies the doctypes this portal surfaces.
required_apps = ["frappe/erpnext", "frappe/hrms"]

# ---------------------------------------------------------------------------
# App switcher tile
# ---------------------------------------------------------------------------
add_to_apps_screen = [
	{
		"name": "fedco_ess",
		"logo": "/assets/fedco_ess/images/fedco_ess.svg",
		"title": "Self Service",
		"route": "/ess",
	},
]

# ---------------------------------------------------------------------------
# Portal
# ---------------------------------------------------------------------------
# Surfaces the portal in the logged-in user's menu.
standard_portal_menu_items = [
	{
		"title": "Self Service",
		"route": "/ess",
		"reference_doctype": "",
		"role": "Employee",
	},
]

website_route_rules = []

after_install = "fedco_ess.install.after_install"
after_migrate = "fedco_ess.install.after_migrate"

fixtures = []
