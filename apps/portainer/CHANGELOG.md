# CHANGELOG

## 2026-11-26

- Split installation guidance into `help.init` (first-start prerequisites) and `help.login` (sign-in steps).

## 2026-09-30

- Update Portainer CE from `2.34.0` to `2.45.1` (latest stable upstream release; Portainer publishes no `x.x` tag, so exact `x.x.x` pinning is required).
- Align `.env` with the current repository policy: template layout and image-env section banner.
- Drop the deprecated compose `version` field and the `# image:`/`# docs:` source comments, and document the published port inline.
- Declare the Portainer first-run setup token as a `variables.json` `credentials.token` source (`container-log`) with a short `help.login` note.
- Add `apps/portainer/tests/cases.yml` with a dedicated `/api/system/status` reachability check.
- Regenerate `README.md` from `variables.json` and `docker-compose.yml`.

## 2026-10-10

- Replace the fragile setup-token `credentials.container-log` regex model with structured `setup.steps`.
- Model the Portainer bootstrap flow as two login-prep steps: read the setup token from logs, then open the web setup screen.
- Keep `help.login` focused on the final administrator sign-in after the wizard completes.

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

- Remove the unconsumed `setup` block from `variables.json` and align first-run interactive administrator creation with `credentials.none=true` and `help.login`.
