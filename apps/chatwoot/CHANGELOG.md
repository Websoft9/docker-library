# CHANGELOG

## 2026-10-30
- Updated Chatwoot to `v4.19.1` for the upstream security hardening and fixes.

## 2026-10-13
- Upgraded Chatwoot from `v4.8.0` to `v4.18.0` based on the latest stable upstream release and image tag.
- Aligned `.env` and `docker-compose.yml` with current repository policy by converting all variable references to `${VAR}` form and removing upstream source comments from the compose file.
- Removed the packaged long-running migrate service and made the main app container run the upstream-required `rails db:chatwoot_prepare` step before starting Puma so first deploy and upgrades stay self-consistent.
- Added a main-container healthcheck and an app-specific API readiness check at `/api`.
- Refreshed `variables.json`, added app help text for first-run administrator creation, and regenerated the package README.
