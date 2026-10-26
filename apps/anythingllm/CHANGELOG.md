# CHANGELOG

## 2026-10-26

- Update AnythingLLM from 1.17 to 1.18 using the stable upstream image tag.

## 2026-10-13

- Update AnythingLLM from 1.16 to 1.17 using the stable upstream image tag.
- Refresh `variables.json` upstream compose and env sources to the raw official files so drift checks resolve correctly.
- Add `tests/cases.yml` with an app-specific `/api/ping` reachability check.
- Align `.env` with the current repository layout while keeping the package's minimal AnythingLLM-specific settings.

## 2026-09-02

- Update AnythingLLM from 1.8 to 1.16 (minor float tag).
- Remove legacy `# docs:` source comments from `docker-compose.yml` and move the upstream compose/env/docs links into `variables.json` `upstream`.
- Add an inline `# Web Console` purpose comment to the published port and use braced `${VAR}` references in `docker-compose.yml`.
- Author a real AnythingLLM usage guide in the README `Usage` section instead of template or Notes-derived placeholder text.
