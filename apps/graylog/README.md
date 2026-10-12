# Graylog on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Graylog**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### First-Time Initialization

1. On the first startup, read the temporary admin password from the container logs: `docker logs graylog`.
2. Open the login URL and sign in as `admin` with that temporary password to finish the setup wizard.
3. After initialization completes, log in with the account and password shown in the **Access** tab (`admin` / `admin`).

### Usage

1. Make sure you are signed in to the Graylog admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Graylog Docker image](https://hub.docker.com/r/graylog/graylog) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 7.1.


### Ports

| Purpose | Port |
| --- | --- |


### Data Directory


- `mongodb_data` → `/data/db`
- `graylog_data` → `/usr/share/graylog/data/`
- `graylog_plugin` → `/usr/share/graylog/plugin`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Graylog Administrator Guide](https://support.websoft9.com/docs/graylog) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/graylog/graylog)

- [Official docs](https://go2docs.graylog.org/current/downloading_and_installing_graylog/docker_installation.htm)

- [Official docs](https://go2docs.graylog.org/current/upgrading_graylog/upgrading_graylog_in_docker.htm)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
