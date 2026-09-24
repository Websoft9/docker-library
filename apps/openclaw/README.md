# OpenClaw on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **OpenClaw**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the OpenClaw admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [OpenClaw Docker image](https://ghcr.io/openclaw/openclaw) and makes some improvements below.

<!-- W9_NOTE_START -->
- Leave `OPENCLAW_PUBLIC_SCHEME` and `OPENCLAW_PUBLIC_ORIGIN` empty for direct IP/LAN access. For domain access, set `OPENCLAW_PUBLIC_SCHEME=https` to derive the exact browser origin from `W9_URL`, or set `OPENCLAW_PUBLIC_ORIGIN` to an exact override before recreating the app.
- The package re-applies `gateway.publicOrigin` and `gateway.controlUi.allowedOrigins` on every recreate through `openclaw-init`, so domain-related config changes do not get stuck in the persisted volume.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 2026.9.6.


### Ports

| Purpose | Port |
| --- | --- |
| Gateway Control UI and WebSocket API | 18789 |
| Browser/bridge control service | 18790 |


### Data Directory


Data is persisted in the `openclaw_data` volume, mounted at `/home/node/.openclaw`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/openclaw.json` to `/seed/openclaw.json`.


## References

- [OpenClaw Administrator Guide](https://support.websoft9.com/docs/openclaw) by Websoft9

- [GHCR image](https://ghcr.io/openclaw/openclaw)

- [Releases](https://github.com/openclaw/openclaw/releases)

- [Official docs](https://docs.openclaw.ai/install/docker)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
