# Vaultwarden on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Vaultwarden**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Vaultwarden URL from the Websoft9 **Access** tab.
2. Create the first account in the web vault, then set `SIGNUPS_ALLOWED=false` in `.env` and rebuild to stop open registration.
3. The admin page is at `/admin`; sign in with the `ADMIN_TOKEN` value from `.env`.

### Change Password

The admin token is `W9_POWER_PASSWORD` in `.env`; update it and rebuild to rotate it. User account passwords are managed inside the web vault.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Vaultwarden Docker image](https://hub.docker.com/r/vaultwarden/server) and makes some improvements below.

<!-- W9_NOTE_START -->
Vaultwarden needs HTTPS for the browser Web Crypto API (WebAuthn), so publish it behind a TLS-enabled domain. This package bundles MariaDB 11.4; deployments created on the previous MariaDB 10.4 volume must follow the MariaDB stepwise upgrade path before starting this version.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 1.37.3, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web vault and API | 80 |


### Data Directory


- `vaultwarden_vol` → `/data/`
- `mariadb_vol` → `/var/lib/mysql`
- `/etc/localtime` → `/etc/localtime`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Vaultwarden Administrator Guide](https://support.websoft9.com/docs/vaultwarden) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/vaultwarden/server)

- [Releases](https://github.com/dani-garcia/vaultwarden/releases)

- [GitHub docs](https://github.com/dani-garcia/vaultwarden/wiki)

- [GitHub docs](https://github.com/dani-garcia/vaultwarden/wiki/Enabling-admin-page)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
