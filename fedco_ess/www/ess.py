# Copyright (c) 2026, FEDCO
# License: MIT

"""
Employee Self-Service hub.

A branded landing page that gathers the ESS features into one place. It does
not reimplement leave, attendance, claims or payroll — those are native Frappe
HR doctypes and rebuilding them would mean re-solving problems the framework
has already solved. This page surfaces them, shows the few live figures an
employee actually opens the portal to check, and links out.

Route: /ess
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.throw(_("Please sign in to view your self-service portal."), frappe.PermissionError)

	context.no_cache = 1
	context.show_sidebar = False

	employee = get_employee()
	context.employee = employee
	context.user_fullname = frappe.db.get_value("User", frappe.session.user, "full_name")

	if not employee:
		# A user with no Employee record can still reach the page; showing a
		# clear message beats a stack trace or an empty dashboard.
		context.no_employee = True
		context.tiles = build_tiles(None)
		return context

	context.no_employee = False
	context.leave_balances = get_leave_balances(employee)
	context.pending = get_pending_counts(employee)
	context.latest_payslip = get_latest_payslip(employee)
	context.announcements = get_announcements()
	context.tiles = build_tiles(employee)
	context.approvals = get_approvals_for_manager()

	return context


def get_employee():
	name = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
	if not name:
		return None
	return frappe.get_doc("Employee", name)


# ----------------------------------------------------------------------
# live figures
# ----------------------------------------------------------------------
def get_leave_balances(employee):
	"""Remaining days per leave type for the current allocation period."""
	try:
		from hrms.hr.doctype.leave_application.leave_application import get_leave_balance_on
	except Exception:
		return []

	types = frappe.get_all("Leave Type", pluck="name")
	out = []
	for leave_type in types:
		try:
			balance = get_leave_balance_on(employee.name, leave_type, nowdate())
		except Exception:
			continue
		if flt(balance):
			out.append({"leave_type": leave_type, "balance": flt(balance, 1)})
	return sorted(out, key=lambda r: -r["balance"])[:4]


def _count(doctype, filters):
	try:
		return frappe.db.count(doctype, filters)
	except Exception:
		return 0


def get_pending_counts(employee):
	"""What the employee has in flight right now."""
	return {
		"leave": _count("Leave Application", {"employee": employee.name, "docstatus": 0}),
		"claims": _count("Expense Claim", {"employee": employee.name, "docstatus": 0}),
		"advances": _count("Employee Advance", {"employee": employee.name, "docstatus": 0}),
		"timesheets": _count("Timesheet", {"employee": employee.name, "docstatus": 0}),
	}


def get_latest_payslip(employee):
	rows = frappe.get_all(
		"Salary Slip",
		filters={"employee": employee.name, "docstatus": 1},
		fields=["name", "start_date", "end_date", "net_pay", "currency"],
		order_by="end_date desc",
		limit=1,
	)
	return rows[0] if rows else None


def get_announcements(limit=4):
	"""HR announcements, if the doctype has been installed."""
	if not frappe.db.exists("DocType", "HR Announcement"):
		return []
	try:
		return frappe.get_all(
			"HR Announcement",
			filters={"published": 1},
			fields=["name", "title", "posted_on", "category"],
			order_by="posted_on desc",
			limit=limit,
		)
	except Exception:
		return []


def get_approvals_for_manager():
	"""Documents awaiting this user's approval, across the usual suspects."""
	pending = []
	checks = [
		("Leave Application", {"leave_approver": frappe.session.user, "docstatus": 0}),
		("Expense Claim", {"expense_approver": frappe.session.user, "docstatus": 0}),
	]
	for doctype, filters in checks:
		count = _count(doctype, filters)
		if count:
			pending.append({"doctype": doctype, "count": count})
	return pending


# ----------------------------------------------------------------------
# the tile grid
# ----------------------------------------------------------------------
def build_tiles(employee):
	"""
	Every ESS feature, grouped.

	`route` points at the native list or form. A tile whose doctype is not
	installed is dropped rather than rendered as a dead link.
	"""
	groups = [
		{
			"title": "My Profile",
			"items": [
				("Employee Profile", "user", "/app/employee/" + (employee.name if employee else ""), "Employee"),
				("Personal Information", "id-card", "/app/employee/" + (employee.name if employee else ""), "Employee"),
				("Emergency Contacts", "phone", "/app/employee/" + (employee.name if employee else ""), "Employee"),
				("My Documents", "folder", "/app/file", None),
				("Company Directory", "users", "/directory", None),
			],
		},
		{
			"title": "Leave & Attendance",
			"items": [
				("Apply for Leave", "calendar-plus", "/app/leave-application/new", "Leave Application"),
				("Leave Balance", "gauge", "/app/leave-application", "Leave Application"),
				("Leave History", "history", "/app/leave-application", "Leave Application"),
				("Check In / Out", "clock", "/app/employee-checkin", "Employee Checkin"),
				("Attendance History", "calendar-check", "/app/attendance", "Attendance"),
				("My Shift", "sun", "/app/shift-assignment", "Shift Assignment"),
				("Shift Request", "shuffle", "/app/shift-request/new", "Shift Request"),
			],
		},
		{
			"title": "Time & Pay",
			"items": [
				("Submit Timesheet", "timer", "/app/timesheet/new", "Timesheet"),
				("Overtime Request", "plus-circle", "/app/attendance-request/new", "Attendance Request"),
				("My Payslips", "receipt", "/app/salary-slip", "Salary Slip"),
				("Salary Information", "wallet", "/app/salary-structure-assignment", "Salary Structure Assignment"),
				("Employee Benefits", "gift", "/app/employee-benefit-application", "Employee Benefit Application"),
			],
		},
		{
			"title": "Claims & Requests",
			"items": [
				("New Claim Voucher", "file-text", "/app/expense-claim/new", "Expense Claim"),
				("My Claims", "list", "/app/expense-claim", "Expense Claim"),
				("Cash Advance Request", "banknote", "/app/employee-advance/new", "Employee Advance"),
				("Travel Request", "plane", "/app/travel-request/new", "Travel Request"),
				("Loan Request", "landmark", "/app/loan-application/new", "Loan Application"),
				("HR Service Request", "help-circle", "/app/hr-service-request/new", "HR Service Request"),
				("Training Request", "graduation-cap", "/app/training-request/new", "Training Request"),
			],
		},
		{
			"title": "Performance",
			"items": [
				("My Goals / KRAs", "target", "/app/goal", "Goal"),
				("Self Appraisal", "star", "/app/appraisal", "Appraisal"),
				("Performance Review", "trending-up", "/app/appraisal", "Appraisal"),
			],
		},
		{
			"title": "Company",
			"items": [
				("HR Announcements", "megaphone", "/app/hr-announcement", "HR Announcement"),
				("Policies & HR Documents", "book", "/policies", None),
				("Notifications", "bell", "/app/notification-log", "Notification Log"),
			],
		},
	]

	out = []
	for group in groups:
		items = []
		for label, icon, route, doctype in group["items"]:
			if doctype and not frappe.db.exists("DocType", doctype):
				continue
			items.append({"label": label, "icon": icon, "route": route})
		if items:
			out.append({"title": group["title"], "items": items})
	return out


@frappe.whitelist()
def quick_checkin(log_type="IN"):
	"""Punch in or out from the portal."""
	employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
	if not employee:
		frappe.throw(_("No Employee record is linked to your user account."))

	doc = frappe.new_doc("Employee Checkin")
	doc.employee = employee
	doc.log_type = "OUT" if log_type == "OUT" else "IN"
	doc.time = frappe.utils.now_datetime()
	doc.insert(ignore_permissions=True)
	frappe.db.commit()
	return {"name": doc.name, "log_type": doc.log_type, "time": str(doc.time)}
