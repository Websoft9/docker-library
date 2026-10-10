# Tomcat Notes

> Internal maintenance notes; customer-facing documentation lives in `README.md`.

## Sources

- Official image: https://hub.docker.com/_/tomcat
- Image source: https://github.com/docker-library/tomcat
- Version list: https://hub.docker.com/_/tomcat/tags

## Versions

- `W9_VERSION=11.0-jdk21-temurin`: Tomcat 11 stable line + JDK21 LTS.
- `variables.json` only keeps the temurin variants still published upstream (`11.0` / `10.1` / `9.0`); the official `corretto` variant was removed, so it is no longer listed.
- The `tomcat:/usr/local/tomcat` data volume persists the entire Tomcat directory (including `webapps` and `conf`).

## Startup Mechanism (runtime-app convention)

Follows `docs/runtime-app-spec.md`, consistent with `springboot`, but does **not** introduce a non-root user/permissions sidecar (the official Tomcat image runs as root, and the change would be high-risk).

```
src/entrypoint.sh            # orchestrator, mounted at /opt/websoft9/entrypoint.sh
src/entrypoint.d/*.sh        # in-package hooks, mounted at /opt/websoft9/entrypoint.d (read-only)
src/start.sh                 # default start, mounted at /opt/websoft9/start.sh (read-only)
```

- Hooks come from two locations; a user hook with the same name overrides the in-package hook, they are sorted by filename, and they run on every startup and must be idempotent:
  - In-package: `/opt/websoft9/entrypoint.d`
  - User: `${APP_DIR}/.w9/entrypoint.d`, i.e. `/usr/local/tomcat/.w9/entrypoint.d`
- `APP_DIR=/usr/local/tomcat` (reuses the data volume); users can place `${APP_DIR}/.w9/start.sh` to override the default start.
- Default hook `10-webapps.sh`: `cp -a webapps.dist/. webapps/`, restoring the default ROOT/docs/examples applications.
- `start.sh` uses `exec catalina.sh run`, ensuring Tomcat is PID1 and can receive SIGTERM.
- Differences from runtime-app-spec: no `DATABASE_URL` override, no non-root user.

## Running a WAR Package

Enter the **tomcat** container, download the official sample, and it will auto-extract:

```
cd /usr/local/tomcat/webapps && wget https://tomcat.apache.org/tomcat-11.0-doc/appdev/sample/sample.war
cd /usr/local/tomcat/webapps && wget https://tomcat.apache.org/tomcat-11.0-doc/appdev/sample/sample.war -O ROOT.war
```

`ROOT.war` auto-extracts to the root directory (without a path).

## Tests

- `tests/cases.yml`: in addition to the default adaptive checks (compose-config / container-up / container-healthy / web-access `/`), it adds two `script` cases:
  - `smoke.sh`: verifies the welcome page content, proving the default applications from `10-webapps.sh` have been restored.
  - `war-deploy.sh`: builds a tiny WAR inside the container with `jar`, places it in `webapps/`, waits for auto-extraction, and verifies the context, validating the real WAR deployment path.
- `script` cases run on the **deployment target** by default (over SSH when remote, see `docs/app-tests.md`), so `war-deploy.sh` can use remote `docker exec`; `BASE_URL` is rewritten on the remote to `http://localhost:${W9_HTTP_PORT_SET}`.
