# CHANGELOG

## 2026-10-13

- Rebuilt the package as a standalone GeoServer deployment. The previous package was a WordPress + MariaDB stack mislabeled as GeoServer (`.env`/`docker-compose.yml` carried `WORDPRESS_*` variables and the compose mounted a missing `./src/php_exra.ini`), and `src/` shipped an unrelated GeoServer Cloud microservice stack.
- Switched to the official OSGeo image `docker.osgeo.org/geoserver`, tracked on the rolling `3.0.x` tag.
- Rewrote `.env` for GeoServer: image identity, `W9_HTTP_PORT(_SET)`, built-in `admin` login backed by `W9_POWER_PASSWORD`, `W9_URL`/`W9_URL_REPLACE`, and the GeoServer image variables actually used (`GEOSERVER_ADMIN_USER`, `GEOSERVER_ADMIN_PASSWORD`, `SKIP_DEMO_DATA`, `ROOT_WEBAPP_REDIRECT`, `PROXY_BASE_URL`, `EXTRA_JAVA_OPTS`).
- Rewrote `docker-compose.yml` to a single GeoServer service with a persistent `geoserver_data` volume mounted at `/opt/geoserver_data` and a container healthcheck.
- Removed the unrelated `src/` GeoServer Cloud stack and the missing `php_exra.ini` mount.
- Rebuilt `variables.json` with correct access paths (`/geoserver/web`), requirements, upstream sources, and declarative admin credentials; set `release` to `true` now that the package is deployable.
- Added `tests/cases.yml` covering the web login page and WMS GetCapabilities.
- Regenerated `README.md`.
