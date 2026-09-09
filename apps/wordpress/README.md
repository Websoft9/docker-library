# WordPress on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **WordPress**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the WordPress admin console.
2. Try a core feature.

### Change Password

1. To change the WordPress admin password, sign in to `/wp-admin` and update it from the user profile page.
2. If you cannot sign in, use `wp user update` or reset it directly in the database.
3. Do not rely on changing `.env` alone for an existing site; WordPress stores runtime state in the persistent volume and database.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [WordPress Docker image](https://hub.docker.com/_/wordpress) and makes some improvements below.

<!-- W9_NOTE_START -->
The package mounts `src/websoft9-url.php` with `auto_prepend_file` so `W9_URL` can override `WP_HOME` and `WP_SITEURL` at runtime when needed.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 7.1, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 80 |


### Data Directory


- `wordpress` → `/var/www/html`
- `mysql_data` → `/var/lib/mysql`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


- `./src/php_exra.ini` → `/usr/local/etc/php/conf.d/php_exra.ini`
- `./src/websoft9-url.php` → `/usr/local/share/websoft9-url.php`



## References

- [WordPress Administrator Guide](https://support.websoft9.com/docs/wordpress) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/wordpress)

- [Releases](https://wordpress.org/news/category/releases/)

- [GitHub docs](https://github.com/docker-library/wordpress)

- [Official docs](https://wordpress.org/documentation/article/requirements/)

- [Official docs](https://make.wordpress.org/hosting/handbook/compatibility)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.

**Startup logs say "WordPress not found ... copying now" or "No 'wp-config.php' found"?**
- Normal first-run behavior: the official image copies WordPress into the empty `/var/www/html` volume and generates `wp-config.php` from the `WORDPRESS_*` variables.
- Only investigate when these lines repeat on every restart (data volume not persisting) or are followed by database / PHP errors.
<!-- W9_TROUBLESHOOT_END -->
