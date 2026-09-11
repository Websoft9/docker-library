## 2026-09-10

- Updated GitLab Community Edition from `18.1.3-ce.0` to `19.3.2-ce.0` by owner request.
- Kept this as an explicit high-risk package update because GitLab official docs require stepped upgrade stops rather than a direct jump from `18.1.x` to `19.3.x`.
- Fixed current package policy drift by declaring `W9_URL_REPLACE=true` and normalizing `.env` and `docker-compose.yml` variable references.
- Aligned the Omnibus config with the published package ports so `external_url` uses `${W9_URL}` and Git SSH clone URLs use `${W9_SSH_PORT_SET}`.
- Kept `gitlab-runner` in the package behind an optional `runner` compose profile so the default deployment stays clean while advanced users can still enable and register it manually.
- Seeded a minimal `src/runner-config.toml` (no deployment-specific parameters) so the optional runner profile starts without the previous `config.toml` error loop.
