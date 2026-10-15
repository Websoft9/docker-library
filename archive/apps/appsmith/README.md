# Appsmith on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Appsmith**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Appsmith admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Appsmith Docker image](https://hub.docker.com/r/appsmith/appsmith-ce) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: v2.3, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |


### Data Directory


Data is persisted in the `appsmith` volume, mounted at `/appsmith-stacks`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Appsmith Administrator Guide](https://support.websoft9.com/docs/appsmith) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/appsmith/appsmith-ce)

- [Releases](https://github.com/appsmithorg/appsmith)

- [Official compose](https://raw.githubusercontent.com/appsmithorg/appsmith/release/deploy/docker/docker-compose.yml)

- [Official env example](https://raw.githubusercontent.com/appsmithorg/appsmith/release/.env.example)

- [Official docs](https://docs.appsmith.com/getting-started/setup/installation-guides/docker)

- [Official docs](https://docs.appsmith.com/getting-started/setup/best-practices)

- [Official docs](https://docs.appsmith.com/getting-started/setup/instance-configuration/custom-mongodb-redis)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
