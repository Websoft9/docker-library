# CHANGELOG

## 2026-11-03

- Limit supported Redis versions to 8.10, 8.2, 7.4, 7.2, and 6.2, plus latest.

## 2026-09-30

- Upgrade Redis community to 8.10.
- Fix `upstream.image` to point at the official Redis image (`hub.docker.com/_/redis`).
- Normalize the package to current conventions: braced `${VAR}` references, documented port purpose, and the current `.env` layout.
- Model the ACL `default` credentials through the `W9_LOGIN_*` pair and add an app-specific ping check in `tests/cases.yml`.
