# CHANGELOG

## 2026-09-08
- Updated n8n to `2.38.4`.
- Replaced deprecated `WEBHOOK_URL` with `N8N_WEBHOOK_URL` and added `N8N_PROXY_HOPS=1` for reverse-proxy deployments.
- Replaced the deprecated `N8N_CONFIG_FILES` timezone setup with `GENERIC_TIMEZONE` and `TZ` environment variables.
- Added explicit n8n defaults for unverified packages, runner task timeout, and compression limits to preserve current behavior across upcoming upstream default changes.
- Normalized `.env` and `docker-compose.yml` to current repository policy and upstream docs.
- Regenerated the README.
