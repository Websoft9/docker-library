# Jitsi on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Jitsi**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Bind a domain to the server and set `PUBLIC_URL` in `.env` to `https://<your-domain>:${W9_HTTPS_PORT_SET}`.
2. Open the Access URL in a browser, start a meeting, and share the room link.
3. Sign in with the generated passwords only if authentication (`ENABLE_AUTH`) is enabled.

> Due to functional limitations, HTTPS must be used and Domain name must be bound, IP address cannot be accessed

### Notes

- HTTPS is required, and Jitsi cannot be reached by bare IP; use a real domain and a valid or self-signed certificate.
- Meeting media uses UDP port `${W9_UDP_PORT_SET}` (default 10000); open it in the firewall/security group.
- Change the component passwords in `.env` (`JICOFO_AUTH_PASSWORD`, `JVB_AUTH_PASSWORD`, ...) and rebuild.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Jitsi Docker image](https://ghcr.io/jitsi/web) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: stable-11248.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console (HTTPS) | 8443 |


### Data Directory


- `web_config` → `/config:Z`
- `web_crontabs` → `/var/spool/cron/crontabs:Z`
- `web_transcripts` → `/usr/share/jitsi-meet/transcripts:Z`
- `prosody_config` → `/config:Z`
- `prosody_plugins_custom` → `/prosody-plugins-custom:Z`
- `jicofo_config` → `/config:Z`
- `jvb_config` → `/config:Z`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Jitsi Administrator Guide](https://support.websoft9.com/docs/jitsi) by Websoft9

- [GHCR image](https://ghcr.io/jitsi/web)

- [Releases](https://github.com/jitsi/docker-jitsi-meet/releases)

- [Official compose](https://github.com/jitsi/docker-jitsi-meet/blob/stable-11248/docker-compose.yml)

- [Official env example](https://github.com/jitsi/docker-jitsi-meet/blob/stable-11248/env.example)

- [Official docs](https://jitsi.github.io/handbook/docs/devops-guide/devops-guide-docker)

- [GitHub docs](https://github.com/jitsi/docker-jitsi-meet)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
