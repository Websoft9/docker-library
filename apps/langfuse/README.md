# Langfuse on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Langfuse**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Langfuse UI and complete the first-run sign-up to create the owner account.
2. Create an organization and a project, then copy the project API keys from **Settings → API Keys**.

### Configuration

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update `NEXTAUTH_URL` / `W9_URL` and the shared secrets in `.env` as needed.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Langfuse Docker image](https://hub.docker.com/r/langfuse/langfuse) and makes some improvements below.

<!-- W9_NOTE_START -->
This package runs the Langfuse v4 docker-compose topology: `langfuse-web` and `langfuse-worker` with PostgreSQL 17, ClickHouse, Redis 7 and MinIO. Only the web console is published; the databases and object storage are internal to the app network. Media uploads that emit browser-side presigned URLs to MinIO may need MinIO exposed separately.

`NEXTAUTH_URL` must match the exact URL users open in the browser. If you change the access URL, update `W9_URL` (or `NEXTAUTH_URL`) in `.env` and rebuild.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 4.59, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 3000 |


### Data Directory


- `clickhouse_data` → `/var/lib/clickhouse`
- `clickhouse_logs` → `/var/log/clickhouse-server`
- `minio_data` → `/data`
- `redis_data` → `/data`
- `postgres_data` → `/var/lib/postgresql/data`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Langfuse Administrator Guide](https://support.websoft9.com/docs/langfuse) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/langfuse/langfuse)

- [Releases](https://github.com/langfuse/langfuse/releases)

- [Official compose](https://github.com/langfuse/langfuse/blob/main/docker-compose.yml)

- [Official docs](https://langfuse.com/self-hosting/deployment/docker-compose)

- [Official docs](https://langfuse.com/self-hosting/configuration)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
