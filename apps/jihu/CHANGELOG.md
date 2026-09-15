# CHANGELOG

## 2026-09-15

- Pinned JiHu GitLab from the floating `latest` tag to `19.3.2`.
- Removed the expired bundled JiHu license (`src/gitlab.license`) and its `initial_license_file` wiring. The expired license aborted the first-boot database migration and prevented GitLab from starting; upload a valid license from the admin area when enterprise features are needed.
- Fixed the published-port mapping by adding `nginx['listen_port'] = 80`. When `W9_URL` includes a port (for example `host:9001`), GitLab derived its nginx listen port from `external_url` and listened on `9001` inside the container while the package publishes `${W9_HTTP_PORT_SET}:80`, so external requests hit an empty container port and were reset.
- Fixed the policy gate: declared `W9_URL_REPLACE=true` and wired `external_url` to `http://${W9_URL}`.
- Fixed the Git SSH clone port so it uses `W9_SSH_PORT_SET` instead of a hard-coded `22`.
- Added `upstream` metadata, `access`, a first-startup-only note, and a login-page test case.
- Normalized `.env` and `docker-compose.yml` to current repository policy (braced references, port comments, no source comments, no obsolete compose version).
- Regenerated the README.
