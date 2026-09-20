# Superset on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Superset**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Superset admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Superset Docker image](https://hub.docker.com/r/apache/superset) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 6.1.0, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 8088 |


### Data Directory


- `superset_home` → `/app/superset_home`
- `redis` → `/data`
- `postgresql` → `/var/lib/postgresql/data`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `W9_LOGIN_PASSWORD`, `ADMIN_PASSWORD`, `SUPERSET_SECRET_KEY` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


- `./src/docker` → `/app/docker`
- `./src/docker/docker-entrypoint-initdb.d` → `/docker-entrypoint-initdb.d`



## References

- [Superset Administrator Guide](https://support.websoft9.com/docs/superset) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/apache/superset)

- [Releases](https://github.com/apache/superset/releases)

- [Official docs](https://superset.apache.org/docs/installation/installing-superset-using-docker-compose)

- [GitHub docs](https://github.com/apache/superset/blob/6.1.0/UPDATING.md)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
