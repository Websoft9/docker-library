# Teleport on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Teleport**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Set `W9_URL` and `proxy_service.public_addr` in `src/config/teleport.yaml` to the domain that resolves to this host.
2. Start the app. On first run it creates the `admin` user automatically.
3. Generate the password setup link with `docker exec <container> /usr/local/bin/tctl users reset admin`, then open it to set the admin password. MFA is disabled; enable it later from the Web UI if needed.

### Change Password

1. Reset the user from inside the container: `docker exec <container> /usr/local/bin/tctl users reset <username>`.
2. Open the printed reset URL to set a new password.
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
