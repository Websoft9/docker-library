#!/bin/bash

set -euo pipefail

APP_DIR=/var/www/html
ENV_LOCAL=${APP_DIR}/.env.local
INSTALL_CATALOG=${APP_DIR}/vendor/akeneo/pim-community-dev/src/Akeneo/Platform/Bundle/InstallerBundle/Resources/fixtures/minimal

render_env_local() {
    cat >"${ENV_LOCAL}" <<EOF
AKENEO_PIM_URL=${AKENEO_PIM_URL}
APP_ENV=${APP_ENV}
APP_DEBUG=${APP_DEBUG}
APP_DEFAULT_LOCALE=${APP_DEFAULT_LOCALE}
APP_SECRET=${APP_SECRET}
APP_DATABASE_HOST=${APP_DATABASE_HOST}
APP_DATABASE_PORT=${APP_DATABASE_PORT}
APP_DATABASE_NAME=${APP_DATABASE_NAME}
APP_DATABASE_USER=${APP_DATABASE_USER}
APP_DATABASE_PASSWORD=${APP_DATABASE_PASSWORD}
APP_INDEX_HOSTS=${APP_INDEX_HOSTS}
EOF
}

wait_for_mysql() {
    until mysqladmin ping -h"${APP_DATABASE_HOST}" -u"${APP_DATABASE_USER}" -p"${APP_DATABASE_PASSWORD}" --silent >/dev/null 2>&1; do
        sleep 3
    done
}

wait_for_elasticsearch() {
    until curl -fsS "http://${APP_INDEX_HOSTS}" >/dev/null 2>&1; do
        sleep 3
    done
}

is_initialized() {
    mysql -h"${APP_DATABASE_HOST}" -u"${APP_DATABASE_USER}" -p"${APP_DATABASE_PASSWORD}" -D"${APP_DATABASE_NAME}" -Nse "SHOW TABLES LIKE 'pim_catalog_product';" 2>/dev/null | grep -q pim_catalog_product
}

prepare_runtime_dirs() {
    mkdir -p \
        "${APP_DIR}/var/cache" \
        "${APP_DIR}/var/logs" \
        "${APP_DIR}/var/file_storage/catalog" \
        "${APP_DIR}/var/file_storage/jobs" \
        "${APP_DIR}/var/file_storage/archive" \
        "${APP_DIR}/var/file_storage/category" \
        "${APP_DIR}/var/file_storage/catalogs_mapping"
    chown -R www-data:www-data "${APP_DIR}/var"
}

create_admin_if_missing() {
    local exists
    exists=$(mysql -h"${APP_DATABASE_HOST}" -u"${APP_DATABASE_USER}" -p"${APP_DATABASE_PASSWORD}" -D"${APP_DATABASE_NAME}" -Nse "SELECT username FROM oro_user WHERE username='${AKENEO_ADMIN_USER}';" 2>/dev/null || true)

    if [ -z "${AKENEO_ADMIN_USER:-}" ] || [ -z "${AKENEO_ADMIN_PASSWORD:-}" ]; then
        return
    fi

    if [ -n "${exists}" ]; then
        return
    fi

    php bin/console pim:user:create "${AKENEO_ADMIN_USER}" "${AKENEO_ADMIN_PASSWORD}" "${AKENEO_ADMIN_EMAIL:-admin@example.com}" Admin Admin en_US --admin -n --env=prod || true
}

bootstrap_if_needed() {
    render_env_local
    prepare_runtime_dirs
    php bin/console cache:warmup --env=prod

    if is_initialized; then
        return
    fi

    php bin/console pim:installer:db --catalog "${INSTALL_CATALOG}" --env=prod --no-interaction
    chown -R www-data:www-data "${APP_DIR}"
    create_admin_if_missing
}

run_web() {
    php-fpm -D
    exec apachectl -D FOREGROUND
}

run_worker() {
    exec php bin/console messenger:consume ui_job import_export_job data_maintenance_job --env=prod --time-limit=3600 --memory-limit=512M
}

main() {
    local mode=${1:-web}

    cd "${APP_DIR}"
    wait_for_mysql
    wait_for_elasticsearch
    bootstrap_if_needed

    case "${mode}" in
        web)
            run_web
            ;;
        worker)
            run_worker
            ;;
        *)
            exec "$@"
            ;;
    esac
}

main "$@"
