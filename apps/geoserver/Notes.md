# GeoServer

- Image: `docker.osgeo.org/geoserver` (official OSGeo image), tracked on `3.0.x`.
- Web UI: `http://<host>:<W9_HTTP_PORT_SET>/geoserver/web` (default internal port `8080`, context `/geoserver`).
- Login: built-in administrator account `admin` with the password from `W9_POWER_PASSWORD` (`W9_LOGIN_PASSWORD`).
- Data directory: the named volume `geoserver_data` is mounted at `/opt/geoserver_data`; back it up before upgrading.
- Demo data is kept enabled (`SKIP_DEMO_DATA=false`) so the web UI and OGC services work immediately.
- `PROXY_BASE_URL` is wired to `${W9_URL}` for deployments behind a reverse proxy; set `W9_URL` to the public host when `W9_URL_REPLACE` is not applied automatically.
