# Typo3 on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Typo3**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### First-run install

The package runs TYPO3's non-interactive `setup` on first startup, so the database schema, a basic site, and the administrator account are created automatically:

1. Open the app URL and sign in to the backend at `/typo3/` with `W9_LOGIN_USER` / `W9_LOGIN_PASSWORD` from `.env`.
2. Start building content under the auto-generated site.

If `TYPO3_SETUP_ADMIN_PASSWORD` is left empty, first startup falls back to the browser install tool at `/typo3/install.php`; use the bundled MySQL service (host `typo3-mysql`, database/user `typo3`, password `W9_POWER_PASSWORD`).

### Change Password

`W9_LOGIN_PASSWORD` is applied only during the first-run install. To change it later, sign in to the TYPO3 backend at `/typo3/` and update the administrator password under **User Settings**, or reset it from the install tool.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Typo3 Docker image](https://hub.docker.com/r/martinhelmich/typo3) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 13.4, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 80 |


### Data Directory


- `typo3fileadmin` → `/var/www/html/fileadmin`
- `typo3conf` → `/var/www/html/typo3conf`
- `typo3uploads` → `/var/www/html/uploads`
- `typo3temp` → `/var/www/html/typo3temp`
- `mysql_data` → `/var/lib/mysql`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `TYPO3_DB_DRIVER`, `TYPO3_DB_HOST`, `TYPO3_DB_PORT`, `TYPO3_DB_DBNAME`, `TYPO3_DB_USERNAME`, `TYPO3_DB_PASSWORD`, `TYPO3_SETUP_ADMIN_USERNAME`, `TYPO3_SETUP_ADMIN_PASSWORD`, `TYPO3_SETUP_ADMIN_EMAIL`, `TYPO3_PROJECT_NAME`, `TYPO3_SETUP_CREATE_SITE`, `TYPO3_SERVER_TYPE` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration is overridden by mounting `./src/entrypoint.sh` to `/usr/local/bin/websoft9-entrypoint.sh`.


## References

- [Typo3 Administrator Guide](https://support.websoft9.com/docs/typo3) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/martinhelmich/typo3)

- [Releases](https://github.com/TYPO3/typo3/releases)

- [GitHub docs](https://github.com/martin-helmich/docker-typo3)

- [GitHub docs](https://github.com/TYPO3/typo3)

- [Official docs](https://docs.typo3.org/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
