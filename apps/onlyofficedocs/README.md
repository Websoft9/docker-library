# ONLYOFFICE Docs on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **ONLYOFFICE Docs**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the ONLYOFFICE Docs admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [ONLYOFFICE Docs Docker image](https://hub.docker.com/r/onlyoffice/documentserver) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 9.4, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 80 |


### Data Directory


- `data` → `/var/www/onlyoffice/Data`
- `log` → `/var/log/onlyoffice`
- `lib` → `/var/lib/onlyoffice`
- `fonts` → `/usr/share/fonts/truetype/custom`
- `forgotten` → `/var/lib/onlyoffice/documentserver/App_Data/cache/files/forgotten`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [ONLYOFFICE Docs Administrator Guide](https://support.websoft9.com/docs/onlyofficedocs) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/onlyoffice/documentserver)

- [Releases](https://github.com/ONLYOFFICE/DocumentServer/releases)

- [Official compose](https://raw.githubusercontent.com/ONLYOFFICE/Docker-DocumentServer/master/docker-compose.yml)

- [Official docs](https://helpcenter.onlyoffice.com/docs/installation/docs-community-install-docker.aspx)

- [Official docs](https://api.onlyoffice.com/docs/docs-api/get-started/basic-concepts/)

- [GitHub docs](https://github.com/ONLYOFFICE/Docker-DocumentServer)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
