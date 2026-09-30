#!/usr/bin/env bash
set -euo pipefail

container="${W9_ID:?W9_ID is required}"
password="${W9_POWER_PASSWORD:?W9_POWER_PASSWORD is required}"
admin_port="${W9_ADMIN_PORT_SET:?W9_ADMIN_PORT_SET is required}"

code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "http://localhost:${admin_port}/" || true)"
if [ "${code}" != "200" ]; then
  echo "noVNC admin console returned HTTP ${code}" >&2
  exit 1
fi

actual="$(docker exec "${container}" printenv SE_VNC_PASSWORD 2>/dev/null || true)"
if [ -z "${actual}" ]; then
  echo "SE_VNC_PASSWORD is not set; the admin console is unprotected" >&2
  exit 1
fi
if [ "${actual}" != "${password}" ]; then
  echo "SE_VNC_PASSWORD does not match the package password" >&2
  exit 1
fi

echo "noVNC admin console reachable and password-protected"
