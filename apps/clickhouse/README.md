# ClickHouse on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **ClickHouse**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Play UI from the **Access** tab (`/play`) or connect over HTTP on port 8123.
2. Sign in with the generated admin user, then run SQL, for example: `SELECT version()`.

### Change Password

1. Update `CLICKHOUSE_PASSWORD` (or `W9_POWER_PASSWORD`) in `.env` and save.
2. Rebuild the app so the user is recreated with the new password.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [ClickHouse Docker image](https://hub.docker.com/r/clickhouse/clickhouse-server) and makes some improvements below.

<!-- W9_NOTE_START -->

### ClickHouse SQL

```
show users
show databases
create user websoft9
drop user websoft9
```
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 26.8, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| HTTP interface and Play UI | 8123 |


### Data Directory


- `clickhouse-data` → `/var/lib/clickhouse`
- `clickhouse_logs` → `/var/log/clickhouse-server`
- `clickhouse-config` → `/etc/clickhouse-server/config.d`
- `clickhouse-userconfig` → `/etc/clickhouse-server/users.d`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


- `./src/extra_config.xml` → `/etc/clickhouse-server/config.d/extra_config.xml`
- `./src/extra_user.xml` → `/etc/clickhouse-server/users.d/extra_user.xml`



## References

- [ClickHouse Administrator Guide](https://support.websoft9.com/docs/clickhouse) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/clickhouse/clickhouse-server)

- [Releases](https://github.com/ClickHouse/ClickHouse/releases)

- [GitHub docs](https://github.com/ClickHouse/ClickHouse/tree/master/docker)

- [Official docs](https://clickhouse.com/docs)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
