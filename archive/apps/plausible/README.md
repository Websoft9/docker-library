# Plausible on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Plausible**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Plausible admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Plausible Docker image](https://github.com/plausible/analytics/pkgs/container/community-edition) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: v3.2.1, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 8000 |


### Data Directory


- `db-data` → `/var/lib/postgresql/data`
- `event-data` → `/var/lib/clickhouse`
- `event-logs` → `/var/log/clickhouse-server`
- `plausible-data` → `/var/lib/plausible`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


- `./src/clickhouse/clickhouse-config.xml` → `/etc/clickhouse-server/config.d/logs.xml`
- `./src/clickhouse/clickhouse-user-config.xml` → `/etc/clickhouse-server/users.d/default-profile-low-resources-overrides.xml`



## References

- [Plausible Administrator Guide](https://support.websoft9.com/docs/plausible) by Websoft9

- [Docker Hub image](https://github.com/plausible/analytics/pkgs/container/community-edition)

- [Releases](https://github.com/plausible/analytics/releases)

- [Official compose](https://github.com/plausible/community-edition/blob/v3.2.1/compose.yml)

- [Official docs](https://plausible.io/docs/self-hosting)

- [GitHub docs](https://github.com/plausible/community-edition/blob/v3.2.1/README.md)

- [GitHub docs](https://github.com/plausible/community-edition/wiki/Upgrade-PostgreSQL)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
