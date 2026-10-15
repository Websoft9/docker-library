#!/bin/sh
set -eu

APP_DIR=/var/www/html

wait_for_mariadb() {
  until mariadb-admin ping -h"${PIMCORE_DB_HOST}" -u"${PIMCORE_DB_USER}" -p"${PIMCORE_DB_PASSWORD}" --silent >/dev/null 2>&1; do
    sleep 3
  done
}

bootstrap_project() {
  if [ -f "${APP_DIR}/composer.json" ] && [ -f "${APP_DIR}/vendor/bin/pimcore-install" ]; then
    return
  fi

  tmp_dir="$(mktemp -d)"
  COMPOSER_MEMORY_LIMIT=-1 composer create-project --no-interaction --prefer-dist --no-scripts pimcore/skeleton "${tmp_dir}" "${PIMCORE_SKELETON_VERSION}"
  cp -a "${tmp_dir}/." "${APP_DIR}/"
  rm -rf "${tmp_dir}"
}

configure_project() {
  mkdir -p "${APP_DIR}/config/packages"

  cat >"${APP_DIR}/.env.local" <<EOF
APP_ENV=${PIMCORE_APP_ENV}
PIMCORE_INSTALL_MYSQL_USERNAME=${PIMCORE_DB_USER}
PIMCORE_INSTALL_MYSQL_PASSWORD=${PIMCORE_DB_PASSWORD}
PIMCORE_INSTALL_MYSQL_PORT=${PIMCORE_DB_PORT}
PIMCORE_INSTALL_MYSQL_HOST_SOCKET=${PIMCORE_DB_HOST}
PIMCORE_INSTALL_MYSQL_DATABASE=${PIMCORE_DB_NAME}
EOF

  cp /websoft9-src/messenger.yaml "${APP_DIR}/config/packages/messenger.yaml"
}

main() {
  wait_for_mariadb
  bootstrap_project
  configure_project
}

main "$@"
