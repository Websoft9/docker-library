#!/usr/bin/env bash
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

set -eo pipefail

REQUIREMENTS_LOCAL="/app/docker/requirements-local.txt"

function pipInstall() {
  requirementsFile=$1
  declare -a mirrors=(
    https://pypi.org
    https://pypi.tuna.tsinghua.edu.cn/simple/
    https://pypi.mirrors.ustc.edu.cn/simple/
    https://mirrors.aliyun.com/pypi/simple/
    https://pypi.hustunique.com/
    https://pypi.sdutlinux.org/
    https://pypi.douban.com/simple/
    https://repo.huaweicloud.com/repository/pypi/simple/
  )
  time=-1
  fastMirror=""
  for url in "${mirrors[@]}"; do
    SPEED_DOWNLOAD=$(curl --location --range 0-102400 --max-time 8 --silent --write-out %{speed_download} --output /dev/null "${url}")
    if [ $(echo "${SPEED_DOWNLOAD} > ${time}" | bc) -ne 0 ]; then
      time=${SPEED_DOWNLOAD}
      fastMirror=${url}
    fi
  done
  echo "choose the url: ${fastMirror}"
  pip install -r ${requirementsFile} -i ${fastMirror}
}

function retry {
  local retries=$1
  shift

  local count=0
  until "$@"; do
    exit=$?
    wait=$((2 ** $count))
    count=$(($count + 1))
    if [ $count -lt $retries ]; then
      echo "Retry $count/$retries exited $exit, retrying in $wait seconds..."
      sleep $wait
    else
      echo "Retry $count/$retries exited $exit, no more retries left."
      return $exit
    fi
  done
  return 0
}

# If Cypress run – overwrite the password for admin and export env variables
if [ "$CYPRESS_CONFIG" == "true" ]; then
    export SUPERSET_CONFIG=tests.integration_tests.superset_test_config
    export SUPERSET_TESTENV=true
    export ENABLE_REACT_CRUD_VIEWS=true
    export SUPERSET__SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://superset:superset@db:5432/superset
fi
#
# Make sure we have dev requirements installed
#
if [ -f "${REQUIREMENTS_LOCAL}" ]; then
  echo "Installing local overrides at ${REQUIREMENTS_LOCAL}"
  retry 3 pipInstall "${REQUIREMENTS_LOCAL}"
else
  echo "Skipping local overrides"
fi

if [[ "${1}" == "worker" ]]; then
  echo "Starting Celery worker..."
  celery --app=superset.tasks.celery_app:app worker -Ofair -l INFO
elif [[ "${1}" == "beat" ]]; then
  echo "Starting Celery beat..."
  celery --app=superset.tasks.celery_app:app beat --pidfile /tmp/celerybeat.pid -l INFO -s "${SUPERSET_HOME}"/celerybeat-schedule
elif [[ "${1}" == "app" ]]; then
  echo "Starting web app..."
  flask run -p 8088 --with-threads --reload --debugger --host=0.0.0.0
elif [[ "${1}" == "app-gunicorn" ]]; then
  echo "Starting web app..."
  /app/docker/docker-entrypoint.sh
fi
