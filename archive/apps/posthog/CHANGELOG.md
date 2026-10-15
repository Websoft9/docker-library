# CHANGELOG

## 2026-10-09

- Replaced the placeholder WordPress/Discuz files with a real PostHog self-hosted Compose package.
- Added PostHog upstream metadata, runtime environment wiring, and access metadata.
- Added compose helper scripts for PostHog startup and migration flow.

## 2026-10-12

- Restored PostHog from `archive/apps/` back to active maintenance.
- Switched the package to an upstream-shaped network model: internal services stay on the Compose-private network and only the `proxy` entrypoint joins `websoft9`.
- Removed fixed `container_name` assignments so multi-instance isolation can rely on the Compose project name instead of per-service naming.
- Updated the default `ENCRYPTION_SALT_KEYS` to a valid 32-character value and documented the `openssl rand -hex 16` generation requirement.
