# CHANGELOG

## 2026-09-30

- Upgrade Redmine community to 7.0.
- Bump the bundled MySQL dependency from 5.7 to 8.0 (Redmine 7.0 supports MySQL 8.0-8.4).
- Normalize the package to current conventions: braced `${VAR}` references, documented port purpose, upstream env vars moved to `.env`, and a sourced `SECRET_KEY_BASE`.
- Add an authenticated admin-login check in `tests/cases.yml`.
