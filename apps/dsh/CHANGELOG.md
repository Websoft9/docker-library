# CHANGELOG

## 2026-09-28
- Add the initial DeepSeek Harness app package.
- Build a custom image from the official `node:22-slim` base image and the upstream `@deepseek-ai/dsh` npm package.
- Package the Web UI as a single-container deployment with persistent `DSH_HOME` and workspace volumes.
- Add an internal Nginx reverse proxy because upstream intentionally refuses direct `0.0.0.0` binding for `dsh web`.
- Document the token-based first login flow and record it as a container-log credential hint.
- Preserve external Host/Origin headers and pass `W9_URL` as a trusted host so browser API calls do not fail with HTTP 403.
- Add optional `DSH_TRUSTED_HOSTS` support for multi-domain or forwarded-port access.
- Enable `W9_URL_REPLACE=true` and default `DSH_TRUSTED_HOSTS` to `${W9_URL}` so Websoft9 URL changes flow into DSH's browser trust configuration.
- Add install-time `W9_DEEPSEEK_API_KEY_SET` and map it to `DEEPSEEK_API_KEY` for the container.
- Rename the app id from `deepseekharness` to `dsh`, including the package path, `W9_ID`, image repo, and named volumes.
- Patch the installed DSH web client and inject `window.__DSH_LOCAL_APP__` so public-browser access can open Models/settings pages without an SSH tunnel.
- Remove `build` from `docker-compose.yml` so deployment consumes a prebuilt image and keeps image build responsibility separate from runtime compose usage.
