# Prestashop on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Prestashop**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Prestashop admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Prestashop Docker image](https://hub.docker.com/r/prestashop/prestashop) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 9.1, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 80 |


### Data Directory


- `prestashop` → `/var/www/html`
- `mysql_data` → `/var/lib/mysql`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `ADMIN_MAIL`, `ADMIN_PASSWD` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration is overridden by mounting `./src/remove-install.sh` to `/tmp/init-scripts/remove-install.sh`.


## References

- [Prestashop Administrator Guide](https://support.websoft9.com/docs/prestashop) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/prestashop/prestashop)

- [Releases](https://github.com/PrestaShop/PrestaShop/releases)

- [Official compose](https://devdocs.prestashop-project.org/9/basics/installation/environments/docker/)

- [GitHub docs](https://github.com/PrestaShop/docker)

- [Official docs](https://devdocs.prestashop-project.org/)

- [Official docs](https://docs.prestashop-project.org/)

- [Official docs](https://devdocs.prestashop-project.org/9/basics/installation/system-requirements/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
