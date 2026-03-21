#!/bin/bash
# create-site.sh — one-shot ERPNext + HRMS site initializer.
#
# HRMS is installed from a locally pre-downloaded copy at ./src/hrms/
# (mounted read-only at /opt/hrms-src). No runtime GitHub access needed.
#
# Before first `docker compose up`, place HRMS source code into src/hrms/:
#   git clone --depth 1 --branch version-16 https://github.com/frappe/hrms src/hrms
set -e

# ── 1. Wait for infrastructure ────────────────────────────────────────────────
wait-for-it -t 120 "${W9_ID}-mariadb:3306"
wait-for-it -t 120 "${W9_ID}-redis-cache:6379"
wait-for-it -t 120 "${W9_ID}-redis-queue:6379"

# ── 2. Wait for configurator to write common_site_config.json ─────────────────
export start=$(date +%s)
until [[ -n $(grep -hs ^ sites/common_site_config.json | jq -r ".db_host // empty") ]] && \
      [[ -n $(grep -hs ^ sites/common_site_config.json | jq -r ".redis_cache // empty") ]] && \
      [[ -n $(grep -hs ^ sites/common_site_config.json | jq -r ".redis_queue // empty") ]]; do
  echo "Waiting for sites/common_site_config.json..."
  sleep 5
  if (( $(date +%s) - start > 120 )); then
    echo "ERROR: timed out waiting for common_site_config.json"
    exit 1
  fi
done
echo "common_site_config.json ready"

# ── 3. Create site with ERPNext (official pattern, idempotent) ────────────────
if [ ! -d sites/frontend ]; then
  bench new-site \
    --mariadb-user-host-login-scope='%' \
    --admin-password="${W9_LOGIN_PASSWORD}" \
    --db-root-username=root \
    --db-root-password="${W9_LOGIN_PASSWORD}" \
    --install-app erpnext \
    --set-default frontend
else
  echo "Site frontend already exists, skipping"
fi

# ── 4. Copy pre-downloaded HRMS and register into Python env ──────────────────
# Must happen after bench new-site so the Python env is fully initialized.
if [ ! -d apps/hrms ]; then
  if [ ! -f /opt/hrms-src/setup.py ] && [ ! -f /opt/hrms-src/pyproject.toml ]; then
    echo "ERROR: /opt/hrms-src is empty. Run 'bash src/get-hrms.sh' on the host first."
    exit 1
  fi
  echo "Copying HRMS from local source..."
  cp -a /opt/hrms-src apps/hrms
fi
bench pip install -e apps/hrms
ls -1 apps > sites/apps.txt

# ── 5. Install HRMS on site ───────────────────────────────────────────────────
if ! bench --site frontend list-apps | grep -qx hrms; then
  bench --site frontend install-app hrms
else
  echo "HRMS already installed, skipping"
fi

# ── 6. HRMS static assets ─────────────────────────────────────────────────────
# Keep create-site minimal. HRMS static files are synchronized in frontend
# service startup command before nginx starts.
