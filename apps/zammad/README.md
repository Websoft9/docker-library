# Zammad on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Zammad**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Zammad web console from the **Access** tab.
2. Complete the first-run setup wizard to create the administrator account.
3. Configure an email channel and create your first ticket to confirm the flow.

### Change Password

1. Change the administrator password from the user profile inside Zammad.
2. `W9_POWER_PASSWORD` and `W9_RCODE` seed the bundled PostgreSQL credentials and only take effect on first startup; to rotate them, update the roles in PostgreSQL (or recreate the `postgresql-data` volume) and then rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Zammad Docker image](https://ghcr.io/zammad/zammad) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 7.1, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 8080 |


### Data Directory


- `zammad-storage` → `/opt/zammad/storage`
- `elasticsearch-data` → `/usr/share/elasticsearch/data`
- `redis-data` → `/data`
- `postgresql-data` → `/var/lib/postgresql/data`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `W9_POWER_PASSWORD`, `W9_RCODE` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration is overridden by mounting `./src/postgresql_init.sh` to `/docker-entrypoint-initdb.d/postgresql_init.sh`.


## References

- [Zammad Administrator Guide](https://support.websoft9.com/docs/zammad) by Websoft9

- [GHCR image](https://ghcr.io/zammad/zammad)

- [Releases](https://github.com/zammad/zammad-docker-compose/releases)

- [Official compose](https://github.com/zammad/zammad-docker-compose/blob/v17.2.0/docker-compose.yml)

- [Official env example](https://github.com/zammad/zammad-docker-compose/blob/v17.2.0/.env.dist)

- [Official docs](https://docs.zammad.org/en/latest/install/docker-compose.html)

- [Official docs](https://docs.zammad.org/en/latest/install/docker-compose/environment.html)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
