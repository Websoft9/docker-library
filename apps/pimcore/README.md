# Pimcore on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Pimcore**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Pimcore admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Pimcore Docker image](https://hub.docker.com/r/pimcore/pimcore) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: php8.5-v5.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 80 |


### Data Directory


- `pimcore` → `/var/www/html`
- `mariadb` → `/var/lib/mysql`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


- `./src/nginx.conf` → `/etc/nginx/conf.d/default.conf`
- `./src/bootstrap.sh` → `/usr/local/bin/bootstrap.sh`
- `./src/messenger.yaml` → `/websoft9-src/messenger.yaml`



## References

- [Pimcore Administrator Guide](https://support.websoft9.com/docs/pimcore) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/pimcore/pimcore)

- [Releases](https://github.com/pimcore/pimcore/releases)

- [Official compose](https://github.com/pimcore/skeleton/blob/2024.x/docker-compose.yaml)

- [GitHub docs](https://github.com/pimcore/docker/blob/5.x/README.md)

- [Official docs](https://packagist.org/packages/pimcore/skeleton)

- [Official docs](https://packagist.org/packages/pimcore/pimcore)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
