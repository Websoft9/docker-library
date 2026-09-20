#!/bin/bash
set -euo pipefail

APP_DIR="${APP_DIR:-/var/www/html}"
PACKAGE_HOOKS_DIR="/opt/websoft9/entrypoint.d"
USER_HOOKS_DIR="${APP_DIR}/.w9/entrypoint.d"
USER_START="${APP_DIR}/.w9/start.sh"
BASE_ENTRYPOINT="/usr/local/bin/docker-php-serversideup-entrypoint"

log() {
  echo "[laravel-runtime] $*"
}

run_hooks() {
  local -A hooks=()
  local dir file name

  for dir in "${PACKAGE_HOOKS_DIR}" "${USER_HOOKS_DIR}"; do
    [ -d "${dir}" ] || continue
    for file in "${dir}"/*.sh; do
      [ -e "${file}" ] || continue
      name="$(basename "${file}")"
      hooks["${name}"]="${file}"
    done
  done

  if [ "${#hooks[@]}" -eq 0 ]; then
    return 0
  fi

  while IFS= read -r name; do
    log "hook: ${name}"
    bash "${hooks[${name}]}"
  done < <(printf '%s\n' "${!hooks[@]}" | sort)
}

mkdir -p "${APP_DIR}"
cd "${APP_DIR}"
export APP_DIR

# Map the unified DATABASE_URL to Laravel's DB_CONNECTION/DB_URL so the
# application (and the base image Laravel automations) pick it up.
if [ -n "${DATABASE_URL:-}" ]; then
  _scheme="${DATABASE_URL%%://*}"
  case "$_scheme" in
    postgres|postgresql) _connection="pgsql" ;;
    mysql|mariadb)       _connection="mysql" ;;
    *)
      echo "[laravel-runtime] Unsupported DATABASE_URL scheme: ${_scheme}" >&2
      exit 1
      ;;
  esac
  export DB_CONNECTION="${_connection}"
  export DB_URL="${DATABASE_URL}"
  log "DATABASE_URL detected; using DB_CONNECTION=${DB_CONNECTION}"
fi

run_hooks

if [ -f "${USER_START}" ]; then
  log "starting with user start script: ${USER_START}"
  exec bash "${USER_START}"
fi

# Hand off to the base image entrypoint (runs /etc/entrypoint.d and the CMD).
if [ "$#" -eq 0 ]; then
  set -- frankenphp run --config /etc/frankenphp/Caddyfile --adapter caddyfile
fi
exec "${BASE_ENTRYPOINT}" "$@"
