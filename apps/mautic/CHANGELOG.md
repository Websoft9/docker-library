# CHANGELOG

## 2026-11-04

- Declared internal/external MySQL using the five existing native inputs shared by web, cron, and worker; bundled initialization remains independent.
- Resolved the variable-target-port false positive in the shared validator without changing Compose or `.env`.
- Static configuration checks passed without deployment or live database verification; bundled MySQL 8.0 remains EOL and is not upgraded in this change.

## Release
### Fixes and Enhancements

