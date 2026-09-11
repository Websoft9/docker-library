# PostgreSQL on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **PostgreSQL**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the PostgreSQL admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [PostgreSQL Docker image](https://hub.docker.com/_/postgres) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 18, 17, 16, 15, 14, 13, 12, 11, 9.6, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| PostgreSQL | 5432 |


### Data Directory


- `postgres` → `/var/lib/postgresql/data`
- `backup` → `/backup`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `POSTGRES_DB`, `POSTGRES_PASSWORD`, `POSTGRES_USER` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [PostgreSQL Administrator Guide](https://support.websoft9.com/docs/postgresql) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/postgres)

- [Releases](https://www.postgresql.org/docs/release/)

- [GitHub docs](https://github.com/docker-library/postgres)

- [Official docs](https://www.postgresql.org/docs/)

- [Official docs](https://www.postgresql.org/support/versioning/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
