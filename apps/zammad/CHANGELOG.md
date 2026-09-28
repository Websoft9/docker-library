# CHANGELOG

## 2026-09-20
- Update Zammad from 6.5 to 7.1 and switch the image to the official `ghcr.io/zammad/zammad`.
- Rework `docker-compose.yml` and `.env` to the current upstream stack: PostgreSQL 17, Redis 8.10, Memcached 1.6, and a dedicated non-superuser `zammad` role/database provisioned on first init.
- Bundle Elasticsearch 9 and enable it (`ELASTICSEARCH_ENABLED=true`) so search, reports, and attachment indexing work out of the box; scope the ES index namespace to the instance (`ELASTICSEARCH_NAMESPACE=${W9_ID}`) so multiple deployments can safely share one external ES; administrator account is created through the first-run setup wizard.
- Add `tests/cases.yml` with a guided-setup API smoke check.
