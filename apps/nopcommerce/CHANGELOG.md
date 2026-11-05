# CHANGELOG

## 2026-11-03

- Declared the bundled MySQL dependency for the installation wizard without inventing native connection mappings or external providers.
- Kept runtime configuration and image versions unchanged; the existing MySQL 8.0 EOL risk is not resolved by declaration validation.

## 2026-09-30

- Updated NopCommerce from `4.90.2` to `4.90.8`.
- Normalized `.env` and `docker-compose.yml` to current repository policy, including braced variable references and inline port purpose comments.
- Added app-specific validation coverage with `tests/cases.yml`.
