# Notes

- Upstream Docker is a Tier 1 supported install method. Docker installs do not support `hermes update`; upgrades are done by changing the image tag (`W9_VERSION`).
- The image is large (5 GB+); the first pull can take a while.
- `/opt/data` is the single source of truth (config, `.env`, sessions, skills, memories). Keep it on the named volume; avoid host bind mounts because the SQLite `state.db` runs in WAL mode and can be corrupted on virtiofs/9p mounts.
- The dashboard binds `0.0.0.0:9119` and fails closed without an auth provider. `HERMES_DASHBOARD_BASIC_AUTH_SECRET` must be at least 16 bytes, so `W9_POWER_PASSWORD` must be at least 16 characters.
- The dashboard is the main web UI and the container health check target.
- The OpenAI-compatible API server (`8642`) only starts once an LLM provider key is configured; without a provider the port stays closed. Add `OPENROUTER_API_KEY` (or another provider key) to `.env` and recreate the container to enable it.
- `W9_URL` is declared for the web app but is not wired into upstream config, so `W9_URL_REPLACE` is not set.
