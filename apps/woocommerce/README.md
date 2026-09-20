# WooCommerce on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **WooCommerce**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the WooCommerce admin console.
2. Open the **WooCommerce** menu and complete the store setup wizard.
3. Add a product and run a test order through the storefront.

### Change Password

1. To change the WordPress admin password, sign in to `/wp-admin` and update it from the user profile page.
2. If you cannot sign in, use `wp user update` or reset it directly in the database.
3. Do not rely on changing `.env` alone for an existing site; WordPress stores runtime state in the persistent volume and database.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [WooCommerce Docker image](https://hub.docker.com/_/wordpress) and makes some improvements below.

<!-- W9_NOTE_START -->
The package is based on the official WordPress image and ships a `woocommerce-bootstrap` helper. After the first WordPress site install finishes, the helper installs and activates the WooCommerce plugin, so the store features are enabled by default. The plugin version is controlled by `WOOCOMMERCE_VERSION`.

The package mounts `src/websoft9-url.php` with `auto_prepend_file` so `W9_URL` can override `WP_HOME` and `WP_SITEURL` at runtime when needed. It also ships `src/nginx-proxy.conf`, which the Websoft9 Gateway reads and injects into the Proxy Host `server{}` block to raise the gateway upload limit and apply the platform client rate/concurrency limits.
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


Note: `WOOCOMMERCE_VERSION` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


- `./src/php_exra.ini` → `/usr/local/etc/php/conf.d/php_exra.ini`
- `./src/websoft9-url.php` → `/usr/local/share/websoft9-url.php`
- `./src/configure-woocommerce.sh` → `/usr/local/bin/configure-woocommerce.sh`



## References

- [WooCommerce Administrator Guide](https://support.websoft9.com/docs/woocommerce) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/wordpress)

- [Releases](https://wordpress.org/news/category/releases/)

- [GitHub docs](https://github.com/woocommerce/woocommerce)

- [Official docs](https://woocommerce.com/documentation/woocommerce/getting-started/)

- [Official docs](https://woocommerce.com/document/server-requirements/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
