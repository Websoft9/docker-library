# CHANGELOG

## 2026-09-24
- Update the OpenClaw community package from `2026.3.13-1` to `2026.9.6` (`ghcr.io/openclaw/openclaw`).
- Normalize `.env` and `docker-compose.yml` to current repository policy: braced `${VAR}` references, inline port purpose comments, and removal of inline image/docs source comments.
- Fix the `W9_LOGIN*` declaration by pairing `W9_LOGIN_USER=token` with `W9_LOGIN_PASSWORD`, and wire the Gateway token from `W9_LOGIN_PASSWORD` so the Access tab surfaces a stable token.
- Fill missing `variables.json` fields: `upstream.releases`, `upstream.docs`, `access`, `credentials`, `env`, and `help`.
- Add `tests/cases.yml` with a dedicated Gateway health-endpoint check.
- Regenerate `README.md` from the current repository template.
- Add `OPENCLAW_PUBLIC_ORIGIN` and patch `gateway.publicOrigin` plus `gateway.controlUi.allowedOrigins` during init so domain settings are package-managed and re-applied on every recreate without changing the upstream gateway entrypoint.
- Remove the retired inert `gateway.controlUi.dangerouslyDisableDeviceAuth` seed key from the packaged config.
- Let `OPENCLAW_PUBLIC_ORIGIN` override the exact external origin, and otherwise derive it from `OPENCLAW_PUBLIC_SCHEME` plus `W9_URL` so domain access can follow standard Websoft9 host metadata without hardcoding.
