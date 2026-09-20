#!/bin/sh
set -eu

REALM_MARKER="/data/.realm-created"
ZULIP_MANAGE="/home/zulip/deployments/current/manage.py"

if [ -f "${REALM_MARKER}" ]; then
  exit 0
fi

if [ -z "${W9_ZULIP_REALM_NAME:-}" ] || [ -z "${W9_LOGIN_USER:-}" ] || [ -z "${W9_LOGIN_PASSWORD:-}" ]; then
  echo "Skipping default Zulip organization creation because required W9_ZULIP_REALM_* or W9_LOGIN_* settings are missing."
  exit 0
fi

if su zulip -c "${ZULIP_MANAGE} list_realms | awk 'NR > 2 && \$2 != \"zulipinternal\" { found = 1 } END { exit found ? 0 : 1 }'"; then
  touch "${REALM_MARKER}"
  exit 0
fi

password_file="$(mktemp)"
cleanup() {
  rm -f "${password_file}"
}
trap cleanup EXIT INT TERM
printf '%s' "${W9_LOGIN_PASSWORD}" > "${password_file}"
chown zulip:zulip "${password_file}"
chmod 600 "${password_file}"

echo "Creating default Zulip organization \"${W9_ZULIP_REALM_NAME}\" and owner ${W9_LOGIN_USER} ..."
su zulip -c "${ZULIP_MANAGE} create_realm \"${W9_ZULIP_REALM_NAME}\" \"${W9_LOGIN_USER}\" \"${W9_ZULIP_ADMIN_FULL_NAME:-Administrator}\" --string-id \"${W9_ZULIP_REALM_STRING_ID:-}\" --password-file \"${password_file}\""
touch "${REALM_MARKER}"
