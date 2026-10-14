# CHANGELOG

## 2026-10-13
- Initial QwenPaw community package: QwenPaw **Hub**, the multi-user control plane, so one address can host an administrator and multiple user runtimes.
- Use the official `agentscope/qwenpaw` image directly; no custom image is built.
- Add `src/hub-entrypoint.sh` to install the missing Hub control-plane `docker` SDK and `bubblewrap` on start, seed the first administrator from `W9_LOGIN_USER` / `W9_LOGIN_PASSWORD`, render `hub.yaml` with `public_base_url` from `W9_URL` and the Local backend, and run `qwenpaw hub` as a forced-public bind on port `8000`.
- Add `docker-compose.yml` publishing the Hub console on `${W9_HTTP_PORT_SET}:8000`, with `privileged: true`, the `qwenpaw_data` volume at `/app/working`, and an `/api/version` healthcheck.
- Declare `W9_URL` / `W9_URL_REPLACE=true` and add `QWENPAW_HUB_*` variables for base URL, admin seeding, registration mode, and capacity.
- Fill `variables.json` (upstream, access, requirements, first-startup env, help) and `tests/cases.yml`.
