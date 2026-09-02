# Appwrite on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Appwrite**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Appwrite console at `/console`.
2. Create the first administrator account on initial setup.
3. Create a project and verify the API and console are both reachable.

### Change Password

1. Appwrite administrator accounts are created inside the console, not from package-level `W9_LOGIN_*` variables.
2. Use the Appwrite console flow to change an existing administrator password.
3. For version upgrades that require schema changes, back up data first and then run `docker compose exec appwrite migrate` after the new containers are up.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Appwrite Docker image](https://hub.docker.com/r/appwrite/appwrite) and makes some improvements below.

<!-- W9_NOTE_START -->
Appwrite uses a multi-service self-hosted stack. This package keeps the upstream topology and pins the stack to the stable `1.9.6` release series instead of relying on a floating `latest` tag.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 1.9.6, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| HTTP | 80 |
| HTTPS | 443 |


### Data Directory


- `/var/run/docker.sock` → `/var/run/docker.sock`
- `appwrite_config` → `/storage/config`
- `appwrite_certificates` → `/storage/certificates`
- `appwrite_uploads` → `/storage/uploads`
- `appwrite_imports` → `/storage/imports`
- `appwrite_cache` → `/storage/cache`
- `appwrite_functions` → `/storage/functions`
- `appwrite_sites` → `/storage/sites`
- `appwrite_builds` → `/storage/builds`
- `/tmp` → `/tmp`
- `appwrite_mariadb` → `/var/lib/mysql`
- `appwrite_mongodb` → `/data/db`
- `appwrite_mongodb_keyfile` → `/data/keyfile`
- `appwrite_postgresql` → `/var/lib/postgresql/data`
- `appwrite_models` → `/home/embedder/models`
- `appwrite_redis` → `/data`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Appwrite Administrator Guide](https://support.websoft9.com/docs/appwrite) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/appwrite/appwrite)

- [Releases](https://github.com/appwrite/appwrite/releases)

- [Official compose](https://raw.githubusercontent.com/appwrite/appwrite/1.9.6/docker-compose.yml)

- [Official env example](https://raw.githubusercontent.com/appwrite/appwrite/1.9.6/.env)

- [Official docs](https://appwrite.io/docs/advanced/self-hosting)

- [Official docs](https://appwrite.io/docs/advanced/self-hosting/production/updates)

- [Official docs](https://appwrite.io/docs/advanced/self-hosting/configuration/environment-variables)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs` for `appwrite`, `mongodb`, and `redis` first.

**Upgrade completed but data looks stale?**
- Review the Appwrite release notes and run `docker compose exec appwrite migrate` when the target release requires a migration.
<!-- W9_TROUBLESHOOT_END -->
