# FEDCO Employee Self-Service Portal

A branded ESS hub at `/ess` covering all 35 requested features.

## Scope, stated plainly

**27 of the 35 features are already native in Frappe HR.** Leave, attendance,
timesheets, claims, advances, appraisals, travel, loans and payslips are
working doctypes with permissions, workflows and a mobile PWA behind them.

This portal does **not** reimplement them. It gathers them into one branded
place, shows the handful of live figures an employee actually opens a portal to
check, and links out. Rebuilding leave management would mean re-solving
problems the framework has solved, and would break on every upgrade.

| Status | Count | Features |
|---|---|---|
| Native — surfaced by this portal | 27 | leave, attendance, payslips, claims, advances, appraisals, travel, loans, notifications, documents, shifts, timesheets |
| Partial — native but thin | 4 | overtime requests, training requests, benefits information, employee dashboard |
| Needs building | 4 | HR Service Requests, Company Policies library, Company Directory, HR Announcements |

The four gaps are small doctypes. They are **not** included here — say the word
and I'll build them.

## Install

```bash
cd /cloudclusters/erpnext/frappe-bench
bench get-app https://github.com/YOURUSER/fedco_ess.git
bench --site default install-app fedco_ess
bench --site default migrate
bench build --app fedco_ess
bench --site default clear-cache
bench --site default clear-website-cache
```

Restart web and queue processes, then visit `/ess`.

Requires `erpnext` and `hrms`. The install fails early with a clear message if
either is missing.

## Verify

```python
from fedco_ess.install import diagnose
print(diagnose())
```

Returns the app version, your user, whether an Employee record is linked, and
whether HRMS is present.

## What the page shows

- **Hero** — name, employee number, role, department, and four actions: New
  Claim, Apply for Leave, Check In, Check Out
- **Stat strip** — remaining days per leave type and the last payslip net pay,
  read live
- **In Progress** — draft counts for leave, claims, advances, timesheets
- **Approvals / Announcements** — pending approvals for managers, otherwise
  announcements
- **Tile grid** — every ESS feature, grouped into six sections

Tiles pointing at a doctype that isn't installed are dropped rather than
rendered as dead links, so the page stays honest on a partial install.

## Design

FEDCO palette throughout. Gold appears only on the primary action with ink
text — white on gold is 1.61:1 and fails WCAG. 44px minimum touch targets,
single column under 760px, `prefers-reduced-motion` honoured.

## Permissions

The page requires a signed-in user. A user with no linked Employee record sees
a clear message explaining that HR needs to set **User ID** on their Employee
record, rather than an empty dashboard.

Employees see only their own records — that comes from Frappe HR's existing
permission rules, not from anything here.
