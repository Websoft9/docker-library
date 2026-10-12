# Qdrant on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Qdrant**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Qdrant admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Qdrant Docker image](https://hub.docker.com/r/qdrant/qdrant) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: v1.19.2, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| HTTP API and Web UI | 6333 |
| gRPC API | 6334 |


### Data Directory


Data is persisted in the `qdrant` volume, mounted at `/qdrant/storage`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Qdrant Administrator Guide](https://support.websoft9.com/docs/qdrant) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/qdrant/qdrant)

- [Releases](https://github.com/qdrant/qdrant/releases)

- [GitHub docs](https://github.com/qdrant/qdrant)

- [Official docs](https://qdrant.tech/documentation/quickstart/)

- [Official docs](https://api.qdrant.tech/api-reference/service/healthz)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
