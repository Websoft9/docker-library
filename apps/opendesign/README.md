# OpenDesign on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **OpenDesign**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the OpenDesign admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [OpenDesign Docker image](https://ghcr.io/nexu-io/od) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 0.24.1, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console and API | 7456 |


### Data Directory


Data is persisted in the `opendesign_data` volume, mounted at `/app/.od`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [OpenDesign Administrator Guide](https://support.websoft9.com/docs/opendesign) by Websoft9

- [GHCR image](https://ghcr.io/nexu-io/od)

- [Releases](https://github.com/nexu-io/open-design/releases)

- [Official compose](https://github.com/nexu-io/open-design/blob/main/deploy/docker-compose.yml)

- [GitHub docs](https://github.com/nexu-io/open-design)

- [GitHub docs](https://github.com/nexu-io/open-design/blob/main/deploy/docker-compose.yml)

- [Official docs](https://open-design.ai)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
