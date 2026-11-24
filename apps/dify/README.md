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
This package does not offer external databases. Metadata describes the bundled PostgreSQL main and plugin databases, authenticated Redis, and Weaviate using existing configuration sources. PostgreSQL uses its default `postgres` account; vector-store API keys are not database passwords.

Declarations do not rewrite connection settings, migrate data, or rotate credentials. Existing native connection wiring and normalized references are preserved, as is the Redis environment isolation fix; initialization follows the original application values instead of being separated solely for external databases. Known metadata does not prove complete storage information or live credential validity.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 1.9.2, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 80 |


### Data Directory


- `app-storage` → `/app/api/storage`
- `db-data` → `/var/lib/postgresql/data`
- `redis-data` → `/data`
- `plugin_daemon` → `/app/storage`
- `weaviate` → `/var/lib/weaviate`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


- `./src/sandbox/dependencies` → `/dependencies`
- `./src/sandbox/conf` → `/conf`
- `./src/ssrf_proxy/squid.conf.template` → `/etc/squid/squid.conf.template`
- `./src/ssrf_proxy/docker-entrypoint.sh` → `/docker-entrypoint-mount.sh`
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
