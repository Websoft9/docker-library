# CHANGELOG

## 2026-10-13

- Update ClickHouse from `26.8` to `26.9` based on the latest stable upstream branch tag.
- Fix the app metadata/admin path drift to point at the actual Play UI path `/play`.
- Record first-startup-only ClickHouse init envs and declarative login credential metadata.
- Expand `tests/cases.yml` with an app-specific Play UI reachability check.

## 2026-09-15

- Update ClickHouse to `26.8` (alias `latest`).
- Add `upstream` metadata: releases and docs.
- Remove the obsolete `version:` key and source comments from `docker-compose.yml`, normalize references to `${VAR}`, and clarify the published port comment.
- Add `tests/cases.yml` with a `/ping` check and repository catalog data.
