# Caddy on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Caddy**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Caddy admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Caddy Docker image](https://hub.docker.com/_/caddy) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 2.11, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 80 |


### Data Directory


- `data` → `/data`
- `config` → `/config`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


- `./src/Caddyfile` → `/etc/caddy/Caddyfile`
- `./src/cmd.sh` → `/usr/local/bin/cmd.sh`



## References

- [Caddy Administrator Guide](https://support.websoft9.com/docs/caddy) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/caddy)

- [Releases](https://github.com/caddyserver/caddy/releases)

- [GitHub docs](https://github.com/caddyserver/caddy/releases/tag/v2.11.7)

- [Official docs](https://hub.docker.com/_/caddy)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
