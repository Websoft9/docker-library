# CHANGELOG

## 2026-10-09

- Updated Pimcore packaging to the current `pimcore/pimcore:php8.5-v5` runtime line.
- Reworked the package into a deployable minimal topology with nginx, PHP, MariaDB, and Redis.
- Added first-start skeleton bootstrap logic so the package reaches the upstream installer instead of failing with missing application code.
