#!/bin/bash
set -euo pipefail

WORKSPACE="${APP_DIR:-/workspace}"
cd "$WORKSPACE"

MVN_PROFILE_ARGS=()

# Optional external database. When DATABASE_URL is set it is mapped to the
# Spring datasource properties and the matching Maven/Spring profile is
# enabled (the profile adds the JDBC driver).
if [ -n "${DATABASE_URL:-}" ]; then
  _scheme="${DATABASE_URL%%://*}"
  _rest="${DATABASE_URL#*://}"
  _userinfo="${_rest%%@*}"
  _hostpart="${_rest#*@}"

  _user="${_userinfo%%:*}"
  _pass="${_userinfo#*:}"
  [ "$_pass" = "$_userinfo" ] && _pass=""

  _hostport="${_hostpart%%/*}"
  _dbname="${_hostpart#*/}"
  _host="${_hostport%%:*}"
  _port="${_hostport#*:}"
  [ "$_port" = "$_host" ] && _port=""

  case "$_scheme" in
    postgres|postgresql)
      _spring_profile="postgres"
      _jdbc_scheme="postgresql"
      _default_port="5432"
      ;;
    mysql|mariadb)
      _spring_profile="mysql"
      _jdbc_scheme="mysql"
      _default_port="3306"
      ;;
    *)
      echo "[springboot-runtime] Unsupported DATABASE_URL scheme: ${_scheme}" >&2
      exit 1
      ;;
  esac

  [ -z "$_port" ] && _port="$_default_port"

  export SPRING_DATASOURCE_URL="jdbc:${_jdbc_scheme}://${_host}:${_port}/${_dbname}"
  export SPRING_DATASOURCE_USERNAME="${_user}"
  export SPRING_DATASOURCE_PASSWORD="${_pass}"
  case ",${SPRING_PROFILES_ACTIVE:-}," in
    *,${_spring_profile},*) ;;
    *) export SPRING_PROFILES_ACTIVE="${SPRING_PROFILES_ACTIVE:+${SPRING_PROFILES_ACTIVE},}${_spring_profile}" ;;
  esac
  MVN_PROFILE_ARGS=("-P${_spring_profile}")
  echo "[springboot-runtime] DATABASE_URL detected (${_spring_profile}); using ${SPRING_DATASOURCE_URL}"
fi

exec mvn -q -DskipTests "${MVN_PROFILE_ARGS[@]}" spring-boot:run
