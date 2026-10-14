# Budibase on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Budibase**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Budibase admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Budibase Docker image](https://hub.docker.com/r/budibase/proxy) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 10000 |


### Data Directory


- `plugins` → `/plugins`
- `minio_data` → `/data`
- `couchdb3_data` → `/data`
- `redis_data` → `/data`
- `litellm_data` → `/var/lib/postgresql/data`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `BB_ADMIN_USER_EMAIL`, `BB_ADMIN_USER_PASSWORD` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration is overridden by mounting `./src/litellm_config.yaml` to `/app/config.yaml`.


## References

- [Budibase Administrator Guide](https://support.websoft9.com/docs/budibase) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/budibase/proxy)

- [Releases](https://github.com/Budibase/budibase/releases)

- [Official compose](https://raw.githubusercontent.com/Budibase/budibase/master/hosting/docker-compose.yaml)

- [Official env example](https://raw.githubusercontent.com/Budibase/budibase/master/hosting/.env)

- [Official docs](https://docs.budibase.com/docs/docker-compose)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
