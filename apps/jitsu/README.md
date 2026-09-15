# Jitsu on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Jitsu**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Jitsu Console from the **Access** tab.
2. Sign in with `W9_LOGIN_USER` and `W9_LOGIN_PASSWORD`, then change the password after first login.
3. Create a stream and use the published Ingest URL to send a test event.

### Configuration

1. `JITSU_INGEST_PUBLIC_URL` should match the externally reachable ingest endpoint for SDK and API clients.
2. `SEED_USER_EMAIL` and `SEED_USER_PASSWORD` only seed the first console user on the first startup.
3. This package intentionally deploys the Compose-based core stack only; Kubernetes is still required upstream for full connector syncs, functions, and profile builders.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Jitsu Docker image](https://hub.docker.com/r/jitsucom/console) and makes some improvements below.

<!-- W9_NOTE_START -->
- This package uses the official deprecated Compose topology because upstream does not provide a production Helm chart for the full Kubernetes architecture.
- Upstream documents that feature-complete self-hosting since Jitsu 2.14 requires Kubernetes for the operator, function servers, and connector sync jobs.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 2.15.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 3000 |
| Ingest API | 3049 |


### Data Directory

- `postgres_data` → `/var/lib/postgresql/data`
- `mongodb_data` → `/data/db`
- `clickhouse_data` → `/var/lib/clickhouse`
- `redpanda_data` → `/var/lib/redpanda/data`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `W9_LOGIN_USER`, `W9_LOGIN_PASSWORD`, `W9_POWER_PASSWORD` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Jitsu Administrator Guide](https://support.websoft9.com/docs/jitsu) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/jitsucom/console)

- [Releases](https://github.com/jitsucom/jitsu/releases)

- [Official compose](https://raw.githubusercontent.com/jitsucom/jitsu/newjitsu/docker/docker-compose.yml)

- [Official env example](https://raw.githubusercontent.com/jitsucom/jitsu/newjitsu/docker/.env)

- [GitHub docs](https://github.com/jitsucom/jitsu)

- [Official docs](https://jitsu.com/docs/self-hosting/quick-start)

- [Official docs](https://jitsu.com/docs/self-hosting/production-deployment)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs` for `console`, `bulker`, `rotor`, and `ingest`.

**Ingest endpoint not usable from clients?**
- Ensure `JITSU_INGEST_PUBLIC_URL` matches the externally reachable host and port.
<!-- W9_TROUBLESHOOT_END -->
