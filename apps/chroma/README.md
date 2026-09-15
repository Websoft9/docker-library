# Chroma on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Chroma**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Chroma admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Chroma Docker image](https://hub.docker.com/r/chromadb/chroma) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 1.5.9, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Chroma API | 8000 |


### Data Directory


Data is persisted in the `chroma_data` volume, mounted at `/data`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Chroma Administrator Guide](https://support.websoft9.com/docs/chroma) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/chromadb/chroma)

- [Releases](https://github.com/chroma-core/chroma/releases)

- [Official compose](https://raw.githubusercontent.com/chroma-core/chroma/1.5.9/docker-compose.yml)

- [Official docs](https://docs.trychroma.com/guides/deploy/docker)

- [Official docs](https://docs.trychroma.com/reference/server-env-vars)

- [GitHub docs](https://github.com/chroma-core/chroma/releases/tag/1.5.9)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
