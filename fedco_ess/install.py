# Copyright (c) 2026, FEDCO
# License: MIT

"""Setup for the FEDCO ESS portal."""

import frappe


def after_install():
	setup()


def after_migrate():
	setup()


def setup():
	ensure_employee_role()
	frappe.db.commit()


def ensure_employee_role():
	"""
	The portal link is shown to the Employee role.

	Frappe HR creates this role, but the app can be installed before HR on a
	fresh bench, so it is created here if missing rather than leaving the
	portal menu item pointing at a role that does not exist.
	"""
	if frappe.db.exists("Role", "Employee"):
		return
	try:
		role = frappe.new_doc("Role")
		role.role_name = "Employee"
		role.desk_access = 1
		role.flags.ignore_permissions = True
		role.insert(ignore_permissions=True)
	except Exception:
		frappe.log_error(title="FEDCO ESS: could not create Employee role", message=frappe.get_traceback())


@frappe.whitelist()
def diagnose():
	"""Quick health check for the portal."""
	import fedco_ess

	user = frappe.session.user
	employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
	return {
		"app_version": fedco_ess.__version__,
		"user": user,
		"employee_linked": employee or None,
		"hrms_installed": "hrms" in frappe.get_installed_apps(),
		"route": "/ess",
	}
