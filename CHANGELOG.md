# Changelog

Project-level changes only: architecture, delivery model, tooling, CI, and release machinery. App version updates and package fixes are recorded in `apps/<app>/CHANGELOG.md`.

## 2026-10 — Unreleased

### Added
- Staged initial/login credential metadata in `variables.json`.

### Changed
- Moved the opencode session cleanup script from `build/` to `ci/scripts/` and updated `make opencode-clear` to use it.

### Removed
- Removed the legacy `template/` directory; scaffolds and generated docs now use `metadata/templates/`.
- Removed unused `build/update_readme.py`, `build/update_variables.py`, `build/test_apps.py`, and `build/get_apps_latest_version.py`.
- Removed obsolete workflows: `build_files`, `pull_quest_test`, `pre_merge`, `release`, `release-dev`, `sync_php_files`, and `get_apps_latest_version`.
- Removed `add_apps.json` and its template-scaffold workflow.

## 2026-09

### Added
- Appstore catalog dataset versioning: per-app `updatedAt`, content-hash-based `datasetVersion`, and locale-aware default logos.
- App archive/restore workflow with metadata handoff.

### Fixed
- Catalog pagination stability and production field handling.

## 2026-07 / 2026-08 — 0.8.0 / 0.8.1

### Added
- AI-first delivery model: `AGENTS.md`, `docs/ai-sdlc/`, shared `skills/`, and opencode `/libs-*` commands.
- `libs` CLI as the automation interface for app scaffolding, validation, deployment, scanning, catalog, and appstore sync.
- Appstore publish v2 output model (catalog/library/manifest) with dev/rc/release channels.
- External database support for WordPress and Odoo.
- `make dns-bind`, `make dns-delete`, and `make create-aliyun-ecs`.
- Contentful GraphQL catalog fetching (`build/fetch_catalog.py`).

### Changed
- `library.json` reduced to `Version`; release tags derive from it.
- `websoft9-upgrade` moved to a `make` target.

## 2026-05 — 0.7.13

### Changed
- Appstore publish workflows refactored.

## 2024 — 0.6.0 / 0.7.0

### Added
- Edition and distribution model (`edition` in `variables.json`).
- Unified app template and configuration conventions.
- Library expanded to 100+ applications.

## 2023 — 0.1.0–0.5.x

### Added
- Initial template library.
- Edition support and migration from `w9_name` to `W9_ID`.
