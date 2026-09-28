# Seafile on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Seafile**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Seafile admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Seafile Docker image](https://hub.docker.com/r/seafileltd/seafile-mc) and makes some improvements below.

<!-- W9_NOTE_START -->
Notes:

- Domain mode: set `W9_URL` and `SEAFILE_SERVER_PROTOCOL=https` when the app is served behind an HTTPS gateway. A wrong protocol makes the web UI render blank.
- No-domain mode: set `SEAFILE_EXTERNAL_HOSTPORT` to a reachable `IP:port`, for example `203.0.113.10:9001`.
- The package ships `src/nginx-proxy.conf`, which the Websoft9 Gateway injects to disable response buffering for Seafile's chunked assets. This fixes `ERR_INCOMPLETE_CHUNKED_ENCODING` and blank admin pages behind a domain.
- SeaDoc is not bundled. `.sdoc` is a Seafile-specific format; use OnlyOffice for online editing of office files. OnlyOffice is configured directly in `seahub_settings.py`.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 13.0-latest.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 80 |


### Data Directory


- `seafile-data` → `/shared`
- `mysql-data` → `/var/lib/mysql`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `INIT_SEAFILE_MYSQL_ROOT_PASSWORD`, `INIT_SEAFILE_ADMIN_EMAIL`, `INIT_SEAFILE_ADMIN_PASSWORD` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Seafile Administrator Guide](https://support.websoft9.com/docs/seafile) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/seafileltd/seafile-mc)

- [Official docs](https://manual.seafile.com/latest/setup/setup_ce_by_docker/)

- [Official docs](https://manual.seafile.com/latest/extension/only_office/)

- [Official docs](https://manual.seafile.com/latest/upgrade/upgrade_notes_for_13.0.x/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
