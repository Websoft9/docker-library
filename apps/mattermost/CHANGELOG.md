# CHANGELOG

## 2026-09-30

- Update Mattermost team edition from `11.1` to `11.11` (latest stable upstream release; no major-version jump).
- Align `.env` with the current repository policy: template layout, image-env section banner, and removal of the unused `W9_POWER_PASSWORD`.
- Drop the deprecated compose `version` field and the `# docs:`/`# image:` source comments, and document each published port inline.
- Add `apps/mattermost/tests/cases.yml` with a dedicated `/api/v4/system/ping` reachability check.
- Regenerate `README.md` from `variables.json` and `docker-compose.yml`.
