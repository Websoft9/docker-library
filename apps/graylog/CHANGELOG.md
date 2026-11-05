# CHANGELOG

## 2026-11-04

- Declared only the known internal MongoDB service and graylog database used by Graylog and Data Node; no external databases are offered.
- Left managed Data Node search endpoint, TLS, and credentials unknown rather than guessing OpenSearch or treating commented ports, the management API, or Graylog login credentials as database evidence.
- Kept all runtime files unchanged; partial known metadata does not imply complete storage information or live credential verification.

## 2026-10-16

- Split `variables.json.credentials` into `credentials.initial` (preflight setup password from container logs) and `credentials.login` (steady-state password from `W9_LOGIN_PASSWORD`).

## 2026-10-13

- Upgrade Graylog community from 7.1 to 7.2.
- The bundled Data Node uses the shared `W9_VERSION` tag, so it stays aligned with the Graylog 7.2 release line.
- Keep MongoDB on 7.0: MongoDB 8.0.x exits during startup on Linux kernel 6.19-7.0.13 (MongoDB SERVER-121912 / SERVER-125742), and Graylog 7.2 supports MongoDB 7.x-8.0.x.

## 2026-09-29

- Upgrade Graylog community to 7.1.
- Align the bundled Data Node to the Graylog 7.1 release line.
- Keep MongoDB on 7.0: MongoDB 8.0.x exits during startup on Linux kernel 6.19-7.0.13 (MongoDB SERVER-121912 / SERVER-125742), and Graylog 7.1 supports MongoDB 7.x-8.0.x.
- Fix published UDP port mappings and refresh package metadata and app-specific validation coverage.
- Restore the `W9_LOGIN_USER` / `W9_LOGIN_PASSWORD` compatibility variables and declare the same steady-state `admin` / `admin` credential in `variables.json.credentials` (container-env), plus `help.login` to explain the one-time initialization step.
