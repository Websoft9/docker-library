# Ghost on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Ghost**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### First-Time Setup

1. Open the admin URL in a browser, for example `http://<host>:9001/ghost/`.
2. On first run, create the administrator account (name, email, password) in the setup wizard.
3. After setup completes, sign in to the Ghost admin console with the account you created.

### Usage

1. In the admin console, create a post under **Posts** and publish it.
2. Open the site root URL to verify the published post appears.

### Change Password

1. In the Ghost admin console, open **Settings → Staff** and select your account.
2. Change the password there. Ghost stores the admin password in its own database, not in `.env`.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Ghost Docker image](https://hub.docker.com/_/ghost) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 6.65, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Ghost web site and admin console | 2368 |


### Data Directory


- `ghost` → `/var/lib/ghost`
- `mysql` → `/var/lib/mysql`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Ghost Administrator Guide](https://support.websoft9.com/docs/ghost) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/ghost)

- [Releases](https://github.com/TryGhost/Ghost/releases)

- [Official docs](https://ghost.org/docs/config/)

- [Official docs](https://ghost.org/docs/install/docker/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
