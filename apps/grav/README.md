# Grav CMS on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Grav CMS**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the app URL in a browser to see the Grav site.
2. Open `/admin` and create the first administrator account (username, password, and email).
3. Sign in to the admin console and add pages or install themes and plugins.

### Change Password

1. Sign in to the Grav admin console at `/admin`.
2. Open **Accounts** and edit the administrator account to set a new password.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Grav CMS Docker image](https://hub.docker.com/r/linuxserver/grav) and makes some improvements below.

<!-- W9_NOTE_START -->
Grav stores all content and configuration as files, so the whole site lives in the `grav` volume mounted at `/config`. No separate database container is required.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 2.2.8, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 80 |


### Data Directory


Data is persisted in the `grav` volume, mounted at `/config`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/nginx/default.conf` to `/config/nginx/site-confs/default.conf`.


## References

- [Grav CMS Administrator Guide](https://support.websoft9.com/docs/grav) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/linuxserver/grav)

- [Releases](https://github.com/getgrav/grav/releases)

- [GitHub docs](https://github.com/getgrav/grav)

- [Official docs](https://docs.linuxserver.io/images/docker-grav/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
