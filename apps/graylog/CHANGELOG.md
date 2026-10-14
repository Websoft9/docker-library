# CHANGELOG

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
