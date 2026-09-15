# CHANGELOG

## 2026-09-12
- Updated the RabbitMQ image to `4.3-management`.
- Dropped the EOL `3.13-management` line from the supported versions; only `4.3-management` is supported.
- Fixed the `.env` bare `$W9_POWER_PASSWORD` reference to the braced `${W9_POWER_PASSWORD}` form and added the image environment section.
- Cleaned `docker-compose.yml`: removed the source comments and the obsolete `version` key, and added port purpose comments.
- Removed the orphan `src/get_version.sh`.
- Enriched `variables.json` `upstream` with releases and docs, and recorded the first-startup-only credentials.
- Fixed the `trademark` typo from `RabbitQM` to `RabbitMQ`.
- Replaced the `rabbitmq_config` directory volume with a single read-only `./src/rabbitmq.conf` mount at `/etc/rabbitmq/conf.d/99-websoft9.conf`, so the image defaults are preserved and users edit one versioned file.
- Removed the non-official `rabbitmq_plugins` volume; the official image only declares `/var/lib/rabbitmq`.
- Regenerated the README.
