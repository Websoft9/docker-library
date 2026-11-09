#!/bin/sh
set -eu

docker exec -w /var/www/html "${APP_NAME}" php bin/console about --env=prod
