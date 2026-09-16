#!/bin/bash
set -euo pipefail

APP_DIR="${APP_DIR:-/usr/src/app}"
PACKAGE_HOOKS_DIR="/opt/websoft9/entrypoint.d"
USER_HOOKS_DIR="${APP_DIR}/.w9/entrypoint.d"
PACKAGE_START="/opt/websoft9/start.sh"
USER_START="${APP_DIR}/.w9/start.sh"

log() {
  echo "[nextjs-runtime] $*"
}

detect_package_manager() {
  if [ "${NEXTJS_PACKAGE_MANAGER:-auto}" != "auto" ]; then
    echo "${NEXTJS_PACKAGE_MANAGER}"
    return
  fi

  if [ -f pnpm-lock.yaml ]; then
    echo "pnpm"
  elif [ -f yarn.lock ]; then
    echo "yarn"
  else
    echo "npm"
  fi
}

run_hooks() {
  local -A hooks=()
  local dir file name

  # Package hooks first, then user hooks. A user hook with the same basename
  # replaces the package hook; a new basename is inserted in sort order.
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
export W9_VERSION="${W9_VERSION:-latest}"
export W9_HTTP_PORT="${W9_HTTP_PORT:-3000}"
export NODE_IMAGE_TAG="${NODE_IMAGE_TAG:-}"
export PACKAGE_MANAGER="$(detect_package_manager)"

run_hooks

# Start must be exec'd so the server becomes PID 1 and receives signals.
if [ -f "${USER_START}" ]; then
  log "starting with user start script: ${USER_START}"
  exec bash "${USER_START}"
fi

log "starting with default start script"
exec bash "${PACKAGE_START}"
