# Dolibarr on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Dolibarr**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Dolibarr runs its installer on first start and creates the administrator account from `W9_LOGIN_USER` / `W9_LOGIN_PASSWORD`.
2. Sign in at `/index.php` and complete the initial company setup.
3. Try a core feature.

### Change Password

1. Sign in to Dolibarr and change the password from the user profile.
2. `W9_LOGIN_PASSWORD` seeds the administrator password on first startup; changing `.env` later does not change an existing password.
3. If you cannot sign in, reset the password in the database.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Dolibarr Docker image](https://hub.docker.com/r/tuxgasy/dolibarr) and makes some improvements below.

<!-- W9_NOTE_START -->
The package bundles MariaDB and passes the database connection plus the initial administrator credentials through `.env` (`DOLI_*`). The image installs Dolibarr automatically on first start.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 19.0.2, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 80 |


### Data Directory


- `dolibarr_html` → `/var/www/html`
- `dolibarr_documents` → `/var/www/documents`
- `mariadb` → `/var/lib/mysql`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `W9_LOGIN_PASSWORD` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Dolibarr Administrator Guide](https://support.websoft9.com/docs/dolibarr) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/tuxgasy/dolibarr)

- [GitHub docs](https://github.com/tuxgasy/docker-dolibarr)

- [GitHub docs](https://github.com/Dolibarr/dolibarr)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
