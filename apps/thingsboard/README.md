# ThingsBoard on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **ThingsBoard**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the app URL and sign in with the default System Administrator account `sysadmin@thingsboard.org` / `sysadmin`.
2. The bundled init service loads demo tenants, devices, and dashboards so you can explore the platform right away.

### Change Password

1. Sign in to the ThingsBoard web UI.
2. Open the account menu in the top-right corner, choose **Account**, and change the password.
3. Administrators can reset other users' passwords under **Users**.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [ThingsBoard Docker image](https://hub.docker.com/r/thingsboard/tb-node) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 4.3.1, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 8080 |


### Data Directory


Data is persisted in the `postgres-data` volume, mounted at `/var/lib/postgresql`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [ThingsBoard Administrator Guide](https://support.websoft9.com/docs/thingsboard) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/thingsboard/tb-node)

- [Releases](https://github.com/thingsboard/thingsboard/releases)

- [Official docs](https://thingsboard.io/docs/installation/docker/)

- [GitHub docs](https://github.com/thingsboard/thingsboard)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
