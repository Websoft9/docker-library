# CHANGELOG

## 2026-11-05

- Adapted the official 4.4 Compose layout with its internal web-report service and license-data volume; kept the existing PostgreSQL volume and Web Console mapping. No additional device protocol ports are published.
- Simplified initialization to a single startup script with persistent `/data/.tb-installed` and `/data/.tb-installing` markers. Removed the SQL check service and bootstrap-state volume; a new installation still needs only one `docker compose up -d`.
- Removed the retired demo installation flag; the 4.4 setup wizard creates the administrator and optional demo tenant.
- The success marker is written only after the official installer succeeds. An interrupted attempt blocks automatic retries; the main-service healthcheck requires the success marker and application port.
- Remote fresh installation and retained-data recreation passed with the file-marker scheme; database and installation markers were preserved and the installer was skipped on recreation. Stubbed installer tests cover failure, interruption and existing markers. Existing databases without markers require manual confirmation; backups must preserve the matching database and marker volume together. Owner E2E, report generation, license activation and external connections were not tested.

## 2026-11-04

- Wired native Spring datasource URL and credentials into both the application and installation service.
- Replaced package-only `POSTGRESQL_*` intermediates with independent PostgreSQL initialization inputs and native application inputs, preserving default connections.
- Declared internal/external PostgreSQL; image versions are unchanged and deployment validation was not performed.

## 2026-10-30
### Fixes and Enhancements
- Update ThingsBoard to 4.4.0-latest and expose the optional `TB_LICENSE_SECRET` for licensed deployments.
- Support the 4.4 first-run setup and document its production licensing requirement.

## 2026-09-21
### Fixes and Enhancements
- Update ThingsBoard to 4.3.1 and the bundled PostgreSQL to 18.
- Correct `variables.json` upstream image from `thingsboard/tb-postgres` to `thingsboard/tb-node`; add releases and official docs references.
- Refresh `.env` to the current template layout and add `W9_DB_VERSION`.
- Normalize `docker-compose.yml` references to `${VAR}`, remove image source comments, and annotate the published port.
- Regenerate `README.md` so the advertised version matches `4.3.1`.
- Add `tests/cases.yml` and `tests/check.sh` covering the ThingsBoard REST login.
