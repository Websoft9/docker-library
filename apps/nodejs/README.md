# Node.js on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Node.js**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Node.js admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Node.js Docker image](https://hub.docker.com/_/node) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 26, 26-alpine, 26-slim, 24, 23, 23-alpine, 23-slim, 22, 22-alpine, 22-slim, 21, 21-alpine, 21-slim, 20, 20-alpine, 20-slim, 19, 19-alpine, 19-slim, 18, 18-alpine, 18-slim, 17, 17-alpine, 17-slim.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 8080 |


### Data Directory


Data is persisted in the `app` volume, mounted at `/usr/src/app`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/cmd.sh` to `/usr/src/app/cmd.sh`.


## References

- [Node.js Administrator Guide](https://support.websoft9.com/docs/nodejs) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/node)

- [Official docs](https://hub.docker.com/_/node)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
