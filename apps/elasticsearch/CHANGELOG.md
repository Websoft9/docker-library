# CHANGELOG

## 2026-09-12
- Replaced the legacy `W9_LOGIN_GET_PASSWORD` usage with the literal `W9_LOGIN_PASSWORD`, because Elasticsearch already controls the initial password directly from `ELASTIC_PASSWORD`.
- Normalized `.env` variable references to the braced `${VAR}` form.
- Regenerated the README.
