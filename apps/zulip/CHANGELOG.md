# CHANGELOG

## 2026-11-04

- Declared the internal PostgreSQL and Redis dependencies using their real service names and standard environment sources.
- Preserved Redis authentication from the service's REDIS_PASSWORD environment and startup command; excluded RabbitMQ and out-of-scope Memcached.
- Did not invent unconfirmed external connection mappings; runtime files, first-start configuration, and image versions are unchanged.

## 2026-09-18

- Fixed the first-start organization bootstrap on the 12.x image: the password file is now written as root before being chowned to `zulip`, so the post-setup script no longer fails with `Permission denied` when the container root lacks DAC override.
- Fixed the `create_realm` call to pass all positional arguments together, so Zulip 12.2 no longer rejects the owner email and full name as unrecognized arguments.
- Declared `SETTING_FAKE_EMAIL_DOMAIN=zulip.example.com` so first-start realm creation succeeds when `W9_URL` is an IP address rather than a domain.
- Declared `W9_ADMIN_PATH=/login/` in `.env` and the matching `access` block (web `/`, admin `/login/` on port 443) in `variables.json`.
- Migrated the package from the legacy Docker Hub image line to `ghcr.io/zulip/zulip-server:12.2-0`, updating the compose wiring and 12.x environment variable names so the main container can start again.
- Switched the first-start organization bootstrap from a custom container entrypoint to an official `post-setup.d` script that creates a default organization plus owner account after Zulip finishes initialization.
- Declared first-start organization and login variables in `.env`, documented them in metadata, and normalized compose/env variable references to the braced repository style.
