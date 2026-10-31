# DzzOffice on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **DzzOffice**.
2. In the **Access** tab, get the login URL and credentials.

   No preset administrator credentials are shipped; create the admin account in the setup wizard.

3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### First-Time Setup

1. Open the app and visit `/install/` if the installer does not open automatically.
2. Select MySQL/MariaDB and enter `dzzoffice-mariadb` as the database host, `dzzoffice` as the database and username, and the `W9_POWER_PASSWORD` value from `.env`.
3. Create the initial administrator in the installer; the image does not ship preset administrator credentials.

### Data and Passwords

The `dzzoffice_data` and `mariadb_data` volumes persist the application files and database. Back them up before upgrades or removal. Database credentials are initialized on first startup; changing `W9_POWER_PASSWORD` later does not rotate the existing database password.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [DzzOffice Docker image](https://hub.docker.com/r/xiaohu2023/dzzoffice) and makes some improvements below.

<!-- W9_NOTE_START -->
The first-start database name, user, and password are stored in the MariaDB data volume. Keep the `.env` values consistent with that initialized database.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 2.4.2, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 80 |


### Data Directory


- `dzzoffice_data` → `/var/www/html`
- `mariadb_data` → `/var/lib/mysql`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `W9_POWER_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files

The image entrypoint copies the application source into the `dzzoffice_data` volume when it is empty. Site configuration and uploaded data persist in that volume; back it up before upgrades or removal.


## References

- [DzzOffice Administrator Guide](https://support.websoft9.com/docs/dzzoffice) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/xiaohu2023/dzzoffice)

- [Releases](https://github.com/zyx0814/dzzoffice)

- [Official compose](https://raw.githubusercontent.com/zyx0814/dzzoffice-docker/main/compose/docker-compose.yml)

- [Official env example](https://raw.githubusercontent.com/zyx0814/dzzoffice-docker/main/compose/db.env)

- [GitHub docs](https://github.com/zyx0814/dzzoffice)

- [GitHub docs](https://github.com/zyx0814/dzzoffice-docker)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
