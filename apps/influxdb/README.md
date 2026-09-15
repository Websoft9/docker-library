# InfluxDB on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **InfluxDB**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open `http://<host>:8086` and complete the initial setup to create the administrator account, organization, and bucket.
2. Use the Data Explorer to write and query time-series data, or connect with the `influx` CLI / HTTP API on port `8086`.
3. Manage tokens and buckets under **Load Data** and **Settings**.

### Change Password

InfluxDB manages accounts in the app, not in `.env`. Sign in and change the password under **Settings > Account**. To reset it, use the `influx` CLI or recreate the admin user.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [InfluxDB Docker image](https://hub.docker.com/_/influxdb) and makes some improvements below.

<!-- W9_NOTE_START -->
The image tag is pinned to `2.9`. The `latest` tag currently resolves to the 2.9 line; pin `2.9` for production.

Configuration is declared in `src/config.yml`, mounted to `/etc/influxdb2/config.yml`. Precedence is CLI flags > environment variables > this file; `INFLUXD_*` variables can also be set in `.env`. The mount is read-write because the image entrypoint chowns files in `/etc/influxdb2`.

InfluxDB 2.8 introduced hashed API tokens and a BoltDB schema upgrade. Upgrading from 2.7 or earlier is supported, but downgrading back below 2.8 erases all API tokens, so keep backups before moving an existing instance.

InfluxDB 3.x is available as the `3-core` variant: selecting the `3-core` version deploys `influxdb:3-core` with `docker-compose.3-core.yml` and `.env.3-core` (HTTP API on port `8181`, data in the `influxdb3-data` volume, no built-in UI). The `2.9` and `latest` variants use InfluxDB 2.x with the built-in UI on `8086`.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 2.9, latest, 3-core.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| InfluxDB HTTP API and UI | 8086 |


### Data Directory


Data is persisted in the `influxdb2-data` volume, mounted at `/var/lib/influxdb2`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/config.yml` to `/etc/influxdb2/config.yml`.


## References

- [InfluxDB Administrator Guide](https://support.websoft9.com/docs/influxdb) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/influxdb)

- [Releases](https://github.com/influxdata/influxdb/releases)

- [Official docs](https://docs.influxdata.com/influxdb/v2/install/)

- [Official docs](https://docs.influxdata.com/influxdb/v2/reference/)

- [Official docs](https://docs.influxdata.com/influxdb/v2/admin/)

- [Official docs](https://docs.influxdata.com/influxdb3/core/install/)

- [Official docs](https://docs.influxdata.com/influxdb3/core/get-started/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.

**Need to run the initial setup automatically?**
- Set `DOCKER_INFLUXDB_INIT_MODE=setup` with the `DOCKER_INFLUXDB_INIT_*` variables in `.env` before the first start.
<!-- W9_TROUBLESHOOT_END -->
