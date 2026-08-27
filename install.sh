#!/usr/bin/env bash
# FEDCO ESS installer
set -euo pipefail
SITE="${1:-}"
APP_PATH="${2:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"

if [[ -z "$SITE" ]]; then echo "Usage: ./install.sh <site-name> [path]"; exit 1; fi
if [[ ! -f "sites/common_site_config.json" ]]; then
  echo "ERROR: run from your frappe-bench directory."; exit 1
fi
for dep in erpnext hrms; do
  [[ -d "apps/$dep" ]] || { echo "ERROR: '$dep' is required. bench get-app $dep first."; exit 1; }
done

[[ -d "apps/fedco_ess" ]] || bench get-app fedco_ess "$APP_PATH"
bench --site "$SITE" install-app fedco_ess
bench --site "$SITE" migrate
bench build --app fedco_ess
bench --site "$SITE" clear-cache
bench --site "$SITE" clear-website-cache
bench restart || echo "  (bench restart skipped — restart your processes manually)"

cat <<'DONE'

============================================================
 FEDCO ESS installed.  Visit /ess

 Employees need User ID set on their Employee record for
 personal figures to appear.
============================================================
DONE
