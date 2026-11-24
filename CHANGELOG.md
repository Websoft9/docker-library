# Changelog

Project-level changes only: architecture, delivery model, tooling, CI, and release machinery. App version updates and package fixes are recorded in `apps/<app>/CHANGELOG.md`.

## 2026-11

### Added
- Ordered `variables.json.access[]` port-group contract (`id`, `service`, `port`, `protocol`, `public`, `requireDomain`, `requireHttps`, `rootUrl`, `host`, `mappedPort`, `endpoints`), shared `metadata/access-types.json`, Schema and semantic/policy validation (`app-check --gate access`), and consistent `app-info`/report/README/deploy/test integration.
- Access dictionary delivery in full and incremental library artifacts, content fingerprints/checksums, `appstore-sync` preflight and backup/rollback records, and restore-time validation.
- Local catalog working copy at `metadata/.catalog/` (gitignored) and live `libs catalog-pull --from contentful`, with `--from artifact` kept for published snapshots.

### Changed
- Bumped Appstore `library.schemaVersion` from `"2"` to `"3"` in `metadata/appstore-schema.json` so unupgraded consumers reject incompatible access-migrated snapshots safely.
- Migrated all 146 active apps to `access[]` declarations (`access: []` only for confirmed no-network-entry apps) with literal default Compose host ports and upstream native address/port variables; missing `access` now blocks Schema, CLI checks, restore, and publishing.
- Aligned scaffolding, new/update/restore/deploy skills, canonical access documentation, and regression tests.
- Defined the `public` default-publish policy in `docs/app-access-spec.md` section 4.2: publish only what works immediately after install. Optional receiver, monitoring and maintenance ports in 10 apps are now declared `public: false`, and `public` is a `variables.json` deployment policy only, so upstream compose port mappings stay untouched and consumers apply it with a deploy-time override.
- Restored install-time configurability of the Jitsi JVB media port by driving the host mapping, container listener and advertised SDP port from a single `JVB_PORT` variable.
- Catalog sync is now seed-only: `catalog-push --apply` creates missing entries and refreshes derived machine fields but never rewrites content fields of an existing entry; deliberate replacement requires `--overwrite`. `metadata/catalog/` is no longer tracked, the Contentful sync workflow triggers only on `apps/*/variables.json`, and PR-time catalog diff validation was removed.

### Removed
- Removed deprecated platform port/URL/path variables (`W9_*_PORT_SET`, `W9_HTTP_PORT`, `W9_HTTPS_PORT`, `W9_DB_PORT`, `W9_API_PORT`, `W9_URL`, `W9_URL_REPLACE`, `W9_URL_WITH_PORT`, `W9_ADMIN_PATH`, `W9_LOGIN_ConnectURL`) from all active packages and templates, and removed unconsumed `variables.json.setup` metadata.

## 2026-10

### Added
- Staged initial/login credential metadata in `variables.json`.

### Changed
- Separated Appstore root/catalog/library compatibility contracts from generated content versions using `metadata/appstore-schema.json` (root 2, catalog 1, library 2). Removed `minWebsoft9Version`, forced full library transitions across contracts, and stopped overwriting legacy destinations. Publication validates artifacts independently; consumers own compatibility checks and upgrade decisions.
- Moved the opencode session cleanup script from `build/` to `ci/scripts/` and updated `make opencode-clear` to use it.
- Updated `make opencode-clear` to use the OpenCode V2 session API instead of deleting rows directly from its internal SQLite database.
- Moved `fetch_catalog.py` and `library_publish.py` from `build/` to `ci/scripts/`; the `build/` directory is now removed.

### Removed
- Removed the legacy `template/` directory; scaffolds and generated docs now use `metadata/templates/`.
- Removed unused `build/update_readme.py`, `build/update_variables.py`, `build/test_apps.py`, and `build/get_apps_latest_version.py`.
- Removed obsolete workflows: `build_files`, `pull_quest_test`, `pre_merge`, `release`, `release-dev`, `sync_php_files`, and `get_apps_latest_version`.
- Removed `add_apps.json` and its template-scaffold workflow.
- Removed the unused `build/sync_contentful.py`; Contentful sync now uses `libs catalog-push`.

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
