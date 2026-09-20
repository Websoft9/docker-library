#!/bin/bash
set -euo pipefail

APP_DIR="${APP_DIR:-/workspace}"
PACKAGE_HOOKS_DIR="/opt/websoft9/entrypoint.d"
USER_HOOKS_DIR="${APP_DIR}/.w9/entrypoint.d"
PACKAGE_START="/opt/websoft9/start.sh"
USER_START="${APP_DIR}/.w9/start.sh"

log() {
  echo "[springboot-runtime] $*"
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

run_hooks

# Start must be exec'd so Maven/Spring becomes PID 1 and receives signals.
if [ -f "${USER_START}" ]; then
  log "starting with user start script: ${USER_START}"
  exec bash "${USER_START}"
fi

log "starting with default start script"
exec bash "${PACKAGE_START}"
