# GeoServer

- Image: `docker.osgeo.org/geoserver` (official OSGeo image), tracked on `3.0.x`.
- Web UI: `http://<host>:<published-port>/geoserver/web` (internal port `8080`, context `/geoserver`).
- Login: built-in administrator account `admin` with the password from `W9_POWER_PASSWORD` (`W9_LOGIN_PASSWORD`).
- Data directory: the named volume `geoserver_data` is mounted at `/opt/geoserver_data`; back it up before upgrading.
- Demo data is kept enabled (`SKIP_DEMO_DATA=false`) so the web UI and OGC services work immediately.
- Set `GEOSERVER_PUBLIC_URL` to the public origin; Compose appends `/geoserver` for `PROXY_BASE_URL`.
