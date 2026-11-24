# CHANGELOG

## 2026-11-20

- Set the `calls-tcp` and `calls-udp` port groups (`8443`) to `public: false` per `docs/app-access-spec.md` section 4.2, so the Calls ports are enabled on demand after Calls is turned on in the app. The upstream compose port mappings are left unchanged.

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-11-06
- Update Mattermost Team Edition from `12.0` to `12.1` and PostgreSQL from `14.0` to `15.0` to meet Mattermost 12.1's minimum database requirement.

## 2026-11-03
- Declared the PostgreSQL dependency and existing DSN mapping, preserving SSL and timeout parameters and the W9_RCODE password source.
- Kept the fixed database driver, runtime configuration, and image versions unchanged.

## 2026-10-30

- Update Mattermost Team Edition from `11.11` to `12.0`.

## 2026-10-12

- Pin Mattermost Team Edition from the floating `11.11` line to the current stable patch `11.11.1` for deterministic deployments.
- Add upstream Docker and release-note references to the package metadata.

## 2026-09-30

- Update Mattermost team edition from `11.1` to `11.11` (latest stable upstream release; no major-version jump).
- Align `.env` with the current repository policy: template layout, image-env section banner, and removal of the unused `W9_POWER_PASSWORD`.
- Drop the deprecated compose `version` field and the `# docs:`/`# image:` source comments, and document each published port inline.
- Add `apps/mattermost/tests/cases.yml` with a dedicated `/api/v4/system/ping` reachability check.
- Regenerate `README.md` from `variables.json` and `docker-compose.yml`.
