# Changelog

## 2026-09-20

- Update YouTrack community image from `2025.2.89748` to `2026.2.18991`.
- Remove dead `W9_URL_REPLACE` and `W9_URL_WITH_PORT` helpers that failed the policy gate.
- Normalize `.env` and `docker-compose.yml` to current repository policy, including braced variable references and port purpose comments.
- Raise the documented memory requirement to 1.5 GB to match upstream.
- Declare the first-run Configuration Wizard token as a `container-log` credential source.
- Regenerate README.
