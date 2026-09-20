# Laravel on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Laravel**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Laravel admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Laravel Docker image](https://github.com/laravel/framework) and makes some improvements below.

<!-- W9_NOTE_START -->
### Change Database

Edit the connection in `.env`, then rebuild the app:

- `DB_CONNECTION`: database driver (default `mysql`)
- `DB_HOST`: database host
- `DB_PORT`: database port (default `3306`)
- `DB_DATABASE`: database name
- `DB_USERNAME`: database user
- `DB_PASSWORD`: database password

The app reads these on startup, so a rebuild applies the new connection.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 13.31.0, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 8080 |


### Data Directory


- `laravel_app` → `/var/www/html`
- `mysql_data` → `/var/lib/mysql`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


- `./src/entrypoint.d/10-scaffold.sh` → `/etc/entrypoint.d/10-scaffold.sh`
- `./src/entrypoint.d/20-composer-install.sh` → `/etc/entrypoint.d/20-composer-install.sh`



## References

- [Laravel Administrator Guide](https://support.websoft9.com/docs/laravel) by Websoft9

- [Docker Hub image](https://github.com/laravel/framework)

- [Releases](https://github.com/laravel/framework/releases)

- [Official docs](https://laravel.com/framework/docs/installation)

- [Official docs](https://laravel.com/docs/13.x/deployment)

- [Official docs](https://frankenphp.dev/docs/laravel/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
