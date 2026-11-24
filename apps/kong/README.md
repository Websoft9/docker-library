# Kong Gateway (OSS) on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Kong Gateway (OSS)**.
2. In the **Access** tab, get the login URL and credentials.

3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Kong Gateway (OSS) admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Kong Gateway (OSS) Docker image](https://hub.docker.com/_/kong) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 3.9, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Proxy | 8000 |
| Admin API | 8001 |
| Kong Manager | 8002 |


### Data Directory


Data is persisted in the `kong_tmp_vol` volume, mounted at `/tmp`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/config` to `/opt/kong`.


## References

- [Kong Gateway (OSS) Administrator Guide](https://support.websoft9.com/docs/kong) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/kong)

- [Releases](https://github.com/Kong/kong/releases)

- [Official docs](https://docs.konghq.com/gateway/latest/install/docker/)

- [Official docs](https://docs.konghq.com/gateway/latest/production/environment-variables/)

- [GitHub docs](https://github.com/Kong/docker-kong/tree/master/compose)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
