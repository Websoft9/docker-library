# Akeneo on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Akeneo**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Akeneo admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Akeneo Docker image](https://hub.docker.com/r/websoft9dev/akeneo) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: v2026.4.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 80 |


### Data Directory


- `akeneo_storage` → `/var/www/html/var/file_storage`
- `akeneo_logs` → `/var/www/html/var/logs`
- `mysql` → `/var/lib/mysql`
- `elasticsearch` → `/usr/share/elasticsearch/data`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `AKENEO_ADMIN_USER`, `AKENEO_ADMIN_PASSWORD` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Akeneo Administrator Guide](https://support.websoft9.com/docs/akeneo) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/websoft9dev/akeneo)

- [Releases](https://github.com/akeneo/pim-community-dev)

- [Official compose](https://raw.githubusercontent.com/akeneo/pim-community-dev/v2026.4/docker-compose.yml)

- [Official env example](https://raw.githubusercontent.com/akeneo/pim-community-dev/v2026.4/.env)

- [Official docs](https://packagist.org/packages/akeneo/pim-community-standard)

- [Official docs](https://docs.akeneo.com/master/install_pim/docker/installation_docker.html)

- [Official docs](https://docs.akeneo.com/master/technical_architecture/technical_information/server_side_setup_for_hosting.html)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
