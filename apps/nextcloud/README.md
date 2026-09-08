# Nextcloud on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Nextcloud**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Nextcloud admin console.
2. Try a core feature.

### Change Password

1. Sign in to Nextcloud as an administrator.
2. Change the user's password from the web UI, or run `php occ user:resetpassword <username>` inside the container.
3. Do not rely on changing `.env` after deployment; `NEXTCLOUD_ADMIN_USER` and `NEXTCLOUD_ADMIN_PASSWORD` are only used during the initial installation.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Nextcloud Docker image](https://hub.docker.com/_/nextcloud) and makes some improvements below.

<!-- W9_NOTE_START -->
This package keeps Nextcloud on the official single-node Apache image with a bundled MySQL database. The MySQL service is configured with `READ COMMITTED` isolation and row-based binlog format to match the current Nextcloud database requirements.

The package keeps `NEXTCLOUD_TRUSTED_DOMAINS="*"` by default so first access through the published IP/port works during initial setup and validation. If you deploy behind a real domain or reverse proxy, enable `OVERWRITEHOST=${W9_URL}` and `OVERWRITEPROTOCOL=https` as needed.

When reinstalling or upgrading, keep the bundled MySQL version aligned with Nextcloud's supported database matrix, and confirm the host you use to access the site is accepted by Nextcloud's trusted domains list.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 34.0, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 80 |


### Data Directory


- `nextcloud` → `/var/www/html`
- `nextcloud-data` → `/var/www/html/data`
- `mysql` → `/var/lib/mysql`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `NEXTCLOUD_ADMIN_USER`, `NEXTCLOUD_ADMIN_PASSWORD` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Nextcloud Administrator Guide](https://support.websoft9.com/docs/nextcloud) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/nextcloud)

- [Releases](https://nextcloud.com/changelog/)

- [GitHub docs](https://github.com/nextcloud/docker)

- [Official docs](https://docs.nextcloud.com/server/latest/admin_manual/installation/system_requirements.html)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.

**Forgot or want to reset a password?**
- Nextcloud does not support resetting passwords from environment variables after the initial installation.
- Run the following inside the Nextcloud container, replacing `username`:
  - `docker exec -u www-data -it nextcloud /bin/bash`
  - `php occ user:resetpassword username`
<!-- W9_TROUBLESHOOT_END -->
