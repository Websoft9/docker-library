# Dify on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Dify**.
2. In the **Access** tab, get the login URL and credentials.

3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Dify admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Dify Docker image](https://hub.docker.com/r/langgenius/dify-api) and makes some improvements below.

<!-- W9_NOTE_START -->
This package includes Dify Agent's shell-based local sandbox. Make it available only to trusted users. When deploying outside Websoft9, replace both Agent tokens in `.env` with unique high-entropy values.

Existing installations with Weaviate 1.27.0 data must back up the vector store and complete Dify's [staged Weaviate upgrade](https://docs.dify.ai/en/self-host/deploy/troubleshooting/weaviate-server-migration-path) before starting version 1.39.13. Skipping minor versions is unsupported and can break vector search.

This package does not offer external databases; it uses bundled PostgreSQL, Redis, and Weaviate. Database metadata describes the existing connection sources; it does not rewrite connections, migrate data, or rotate credentials. PostgreSQL uses its default `postgres` account, and the vector-store API key is not a database password.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 1.19.0, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |


### Data Directory


- `app-storage` → `/app/api/storage`
- `db-data` → `/var/lib/postgresql/data`
- `redis-data` → `/data`
- `plugin_daemon` → `/app/storage`
- `dify_agent_local_sandbox_home` → `/home/dify`
- `dify_agent_local_sandbox_workspace` → `/workspace`
- `weaviate` → `/var/lib/weaviate`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


- `./src/sandbox/dependencies` → `/dependencies`
- `./src/sandbox/conf` → `/conf`
- `./src/ssrf_proxy/squid.conf.template` → `/etc/squid/squid.conf.template`
- `./src/ssrf_proxy/docker-entrypoint.sh` → `/docker-entrypoint-mount.sh`
- `./src/agent_ssrf_proxy/squid.conf.template` → `/etc/squid/squid.conf.template`
- `./src/nginx/nginx.conf.template` → `/etc/nginx/nginx.conf.template`
- `./src/nginx/proxy.conf.template` → `/etc/nginx/proxy.conf.template`
- `./src/nginx/https.conf.template` → `/etc/nginx/https.conf.template`
- `./src/nginx/conf.d` → `/etc/nginx/conf.d`
- `./src/nginx/docker-entrypoint.sh` → `/docker-entrypoint-mount.sh`



## References

- [Dify Administrator Guide](https://support.websoft9.com/docs/dify) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/langgenius/dify-api)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
