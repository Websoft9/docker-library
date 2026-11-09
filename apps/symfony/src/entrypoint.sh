#!/bin/bash
set -euo pipefail

APP_DIR="${APP_DIR:-/var/www/html}"
PACKAGE_HOOKS_DIR="/opt/websoft9/entrypoint.d"
USER_HOOKS_DIR="${APP_DIR}/.w9/entrypoint.d"
USER_START="${APP_DIR}/.w9/start.sh"
BASE_ENTRYPOINT="/usr/local/bin/docker-php-serversideup-entrypoint"

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
    echo "[symfony-runtime] hook: ${name}"
    bash "${hooks[${name}]}"
  done < <(printf '%s\n' "${!hooks[@]}" | sort)
}

mkdir -p "${APP_DIR}"
cd "${APP_DIR}"
export APP_DIR

run_hooks

if [ -f "${USER_START}" ]; then
  echo "[symfony-runtime] starting with user start script: ${USER_START}"
  exec bash "${USER_START}"
fi

if [ "$#" -eq 0 ]; then
  set -- frankenphp run --config /etc/frankenphp/Caddyfile --adapter caddyfile
fi
exec "${BASE_ENTRYPOINT}" "$@"
