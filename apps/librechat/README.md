# LibreChat on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **LibreChat**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the LibreChat admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [LibreChat Docker image](https://hub.docker.com/r/librechat/librechat) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: v0.8.7, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 3080 |
| Admin Panel | 3000 |


### Data Directory


- `app-images` → `/app/client/public/images`
- `app-uploads` → `/app/uploads`
- `app-logs` → `/app/logs`
- `app-data` → `/app/data`
- `mongodata` → `/data/db`
- `meilisearch` → `/meili_data`
- `pgdata` → `/var/lib/postgresql/data`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/librechat.yaml` to `/app/librechat.yaml`.


## References

- [LibreChat Administrator Guide](https://support.websoft9.com/docs/librechat) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/librechat/librechat)

- [Releases](https://github.com/danny-avila/LibreChat/releases)

- [Official compose](https://raw.githubusercontent.com/danny-avila/LibreChat/main/docker-compose.yml)

- [Official env example](https://raw.githubusercontent.com/danny-avila/LibreChat/main/.env.example)

- [Official docs](https://www.librechat.ai/docs/local/docker)

- [Official docs](https://www.librechat.ai/docs/configuration/dotenv)

- [GitHub docs](https://github.com/danny-avila/LibreChat)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
