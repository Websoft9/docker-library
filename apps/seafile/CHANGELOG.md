# CHANGELOG

## 2026-11-03

- Declared one MariaDB dependency with three database-name sources, separate initialization and application accounts, and existing native MySQL/MariaDB connection inputs.
- Declared the Redis cache separately using its existing host, port, and password inputs; preserved the actual REDIS_PASSWORD command source, including an explicitly empty value.
- Kept initialization credentials, runtime configuration, and image versions unchanged.

## 2026-09-24

- updated Seafile community package target to `13.0-latest`
- aligned `.env` and `docker-compose.yml` with the official Seafile 13.0 CE Docker env and service shape
- normalized braced variable references and inline port comments for current repository policy
- added app metadata for access paths, first-start-only envs, and upstream docs
- added app-specific test coverage for the login page
- added `SEAFILE_EXTERNAL_HOSTPORT` so domain mode and direct `IP:port` mode can share the same package
- removed the bundled SeaDoc service and its gateway rules; `.sdoc` is a Seafile-specific format with recurring routing issues
- no bundled online-office extension; OnlyOffice and similar integrations are configured directly in `seahub_settings.py`
- added `src/nginx-proxy.conf` with the official reverse-proxy settings (buffering off, HTTP/1.1), fixing `ERR_INCOMPLETE_CHUNKED_ENCODING` and blank admin pages behind the gateway
