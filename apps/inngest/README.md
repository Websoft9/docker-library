# Inngest on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Inngest**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Inngest dashboard at the app URL to confirm the self-hosted server is running.
2. Configure your SDK/application with the `INNGEST_EVENT_KEY` and `INNGEST_SIGNING_KEY` from `.env`, plus `INNGEST_BASE_URL` pointing at this server.

### Configuration

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update `INNGEST_EVENT_KEY` and `INNGEST_SIGNING_KEY` in `.env` (the signing key must be a hex string with an even number of characters).
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Inngest Docker image](https://hub.docker.com/r/inngest/inngest) and makes some improvements below.

<!-- W9_NOTE_START -->
This package runs the single-node Inngest server with bundled PostgreSQL 17 (system data and run history) and Redis 7 (queue and run state). Both dependency services are internal to the app network; only the dashboard/API port and the Connect gateway port are published.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: v1.46.0, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Dashboard and API | 8288 |
| Connect WebSocket gateway | 8289 |


### Data Directory


- `postgres` → `/var/lib/postgresql/data`
- `redis` → `/data`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Inngest Administrator Guide](https://support.websoft9.com/docs/inngest) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/inngest/inngest)

- [Releases](https://github.com/inngest/inngest/releases)

- [Official compose](https://www.inngest.com/docs/self-hosting)

- [Official docs](https://www.inngest.com/docs/self-hosting)

- [GitHub docs](https://github.com/inngest/inngest)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
