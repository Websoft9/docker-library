# Changelog

## 2026-11-04

- Declared the MySQL dependency and existing ZT_MYSQL_* connection inputs, with conservative MySQL-only external support.
- Recorded the actual root-only account and independent initialization password source; runtime configuration and image versions are unchanged.

## 2026-09-20

- Update ZenTao community image from `21.7` to `22.6`.
- Normalize `.env` and `docker-compose.yml` to current repository policy, including braced variable references and dependency tag management.
- Add app-local test coverage metadata for the install-wizard flow.
