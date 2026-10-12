# EspoCRM on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **EspoCRM**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the EspoCRM admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [EspoCRM Docker image](https://hub.docker.com/_/espocrm) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 10.0, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 80 |


### Data Directory


- `mariadb` → `/var/lib/mysql`
- `espocrm-data` → `/var/www/html/data`
- `espocrm-custom` → `/var/www/html/custom`
- `espocrm-custom-client` → `/var/www/html/client/custom`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `ESPOCRM_ADMIN_USERNAME`, `ESPOCRM_ADMIN_PASSWORD`, `ESPOCRM_SITE_URL` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [EspoCRM Administrator Guide](https://support.websoft9.com/docs/espocrm) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/espocrm)

- [Releases](https://github.com/espocrm/espocrm/releases)

- [Official docs](https://docs.espocrm.com/administration/docker/installation/#install-espocrm-with-docker-compose)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
