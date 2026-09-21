# CHANGELOG

## 2026-09-21

- Update Typesense from `29.0` to `30.2` (latest stable upstream release).
- Note the v30 behavior changes: synonyms and overrides become top-level Synonym Sets / Curation Sets and analytics rules change shape; existing data is auto-migrated on upgrade, so take a snapshot before upgrading an existing instance.
- Align `.env` with the current repository policy: braced variable references, template layout, image-env section banner, and removal of the unused `W9_POWER_PASSWORD`.
- Add `apps/typesense/tests/cases.yml` with a `/health` reachability check, and drop the source-comment header from `docker-compose.yml` while adding an inline published-port comment.
- Regenerate `README.md` from `variables.json` and `docker-compose.yml`.
