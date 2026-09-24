# Teleport on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Teleport**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Set `W9_URL` to the domain that resolves to this host, then rebuild or restart the app so the init service regenerates `src/config/teleport.yaml` before Teleport starts.
2. Open `https://<host>:<port>/` and sign in with the username and password from the **Access** tab (`W9_LOGIN_USER` / `W9_LOGIN_PASSWORD` in `.env`). MFA is disabled; enable it later from the Web UI if needed.

### Change Password

1. Change it in the Teleport Web UI; the new password is kept across restarts.
2. To change the initial password before first startup, update `W9_LOGIN_PASSWORD` in `.env` and redeploy. The init service regenerates `src/config/bootstrap.yaml` from the current value.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Teleport Docker image](https://gallery.ecr.aws/gravitational/teleport-distroless) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 18.10, 18.


### Ports

| Purpose | Port |
| --- | --- |
| Teleport Proxy HTTPS (Web UI + API) | 3080 |


### Data Directory


Data is persisted in the `teleport_data` volume, mounted at `/var/lib/teleport`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/config` to `/etc/teleport`.


## References

- [Teleport Administrator Guide](https://support.websoft9.com/docs/teleport) by Websoft9

- [Docker Hub image](https://gallery.ecr.aws/gravitational/teleport-distroless)

- [Releases](https://github.com/gravitational/teleport/releases)

- [Official docs](https://goteleport.com/docs/installation/single-machine/docker/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
