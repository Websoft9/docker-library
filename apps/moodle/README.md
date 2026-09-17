# Moodle on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Moodle**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Access URL and sign in at `/login/index.php` with `MOODLE_USERNAME` / `MOODLE_PASSWORD`.
2. As the site administrator, create a course under **Site administration → Courses** and enrol users.

### PHP Settings

1. Edit `src/php.ini` (mounted to `/usr/local/etc/php/conf.d/zz-websoft9.ini`) and restart the container.
2. Or set `PHP_INI-<name>=<value>` in `.env`, for example `PHP_INI-memory_limit=1024M`.

### Notes

- The image installs Moodle automatically on first start; `MOODLE_*` install variables take effect on first start only.
- Moodle cron runs inside the container automatically.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Moodle Docker image](https://hub.docker.com/r/elestio/moodle) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: v5.2.2, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 80 |


### Data Directory


- `moodle_html` → `/var/www/html`
- `moodle_data` → `/var/moodledata`
- `mariadb_data` → `/var/lib/mysql`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `MOODLE_HOST`, `MOODLE_SITE_NAME`, `MOODLE_USERNAME`, `MOODLE_PASSWORD`, `MOODLE_EMAIL`, `MOODLE_DATABASE_HOST`, `MOODLE_DATABASE_NAME`, `MOODLE_DATABASE_USER`, `MOODLE_DATABASE_PASSWORD` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


- `./src/php.ini` → `/usr/local/etc/php/conf.d/zz-websoft9.ini`
- `./src/disable-sslproxy.sh` → `/docker-entrypoint.d/25-disable-sslproxy.sh`



## References

- [Moodle Administrator Guide](https://support.websoft9.com/docs/moodle) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/elestio/moodle)

- [Releases](https://github.com/moodle/moodle/releases)

- [Official docs](https://docs.moodle.org/en/Installation_quick_guide)

- [GitHub docs](https://github.com/moodle/moodle)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
