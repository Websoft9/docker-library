# Canvas on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Canvas**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Canvas admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Canvas Docker image](https://hub.docker.com/r/websoft9dev/canvas) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 2026-05-20.143.


### Ports

| Purpose | Port |
| --- | --- |


### Data Directory


- `canvas_bundle` → `/usr/src/app/vendor/bundle`
- `canvas_tmp` → `/usr/src/app/tmp`
- `canvas_data` → `/usr/src/app/public/assets`
- `canvas_postgresql` → `/var/lib/postgresql/data`
- `canvas_redis` → `/data`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `CANVAS_LMS_ADMIN_EMAIL`, `CANVAS_LMS_ADMIN_PASSWORD`, `CANVAS_LMS_ACCOUNT_NAME` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


- `./src/database.yml` → `/usr/src/app/config/database.yml`
- `./src/domain.yml` → `/usr/src/app/config/domain.yml`
- `./src/redis.yml` → `/usr/src/app/config/redis.yml`
- `./src/cache_store.yml` → `/usr/src/app/config/cache_store.yml`
- `./src/security.yml` → `/usr/src/app/config/security.yml`
- `./src/outgoing_mail.yml` → `/usr/src/app/config/outgoing_mail.yml`
- `./src/dynamic_settings.yml` → `/usr/src/app/config/dynamic_settings.yml`
- `./src/entrypoint.sh` → `/usr/local/bin/entrypoint.sh`
- `./src/delayed_jobs.yml` → `/usr/src/app/config/delayed_jobs.yml`



## References

- [Canvas Administrator Guide](https://support.websoft9.com/docs/canvas) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/websoft9dev/canvas)

- [Releases](https://github.com/instructure/canvas-lms)

- [Official compose](https://raw.githubusercontent.com/instructure/canvas-lms/master/docker-compose.yml)

- [GitHub docs](https://github.com/instructure/canvas-lms/wiki/Production-Start)

- [Official docs](https://raw.githubusercontent.com/instructure/canvas-lms/master/Dockerfile.production)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
