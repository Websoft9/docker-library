# Checkmate on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Checkmate**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Checkmate web console from the **Access** tab.
2. Register the first account, then add a monitor under **Monitors** and confirm its status turns up.
3. Optionally publish a public status page from **Status Pages**.

### Configuration

1. Set `CLIENT_HOST` to the public URL if it differs from the default, then rebuild.
2. Configure email/notification channels inside the app after signing in.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Checkmate Docker image](https://ghcr.io/bluewave-labs/checkmate) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: v3.12.0, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 52345 |


### Data Directory


Data is persisted in the `mongo_data` volume, mounted at `/data/db`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Checkmate Administrator Guide](https://support.websoft9.com/docs/checkmate) by Websoft9

- [GHCR image](https://ghcr.io/bluewave-labs/checkmate)

- [Releases](https://github.com/bluewave-labs/checkmate/releases)

- [Official compose](https://github.com/bluewave-labs/checkmate/blob/v3.12.0/docker/docker-compose.yaml)

- [Official env example](https://github.com/bluewave-labs/checkmate/blob/v3.12.0/server/.env.example)

- [GitHub docs](https://github.com/bluewave-labs/checkmate)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
