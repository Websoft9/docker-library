# CloudBeaver on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **CloudBeaver**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. CloudBeaver creates the administrator account from `W9_LOGIN_USER` / `W9_LOGIN_PASSWORD` on first start.
2. Sign in and create a database connection.
3. Try a core feature, such as the SQL editor.

### Change Password

1. Sign in to CloudBeaver and change the password from the user profile.
2. `W9_LOGIN_PASSWORD` seeds the administrator password on first startup; changing `.env` later does not change an existing password.
3. If you cannot sign in, reset the password with the upstream admin password recovery procedure.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [CloudBeaver Docker image](https://hub.docker.com/r/dbeaver/cloudbeaver) and makes some improvements below.

<!-- W9_NOTE_START -->
The package passes the server name, the public server URL, and the initial administrator credentials through `.env` (`CB_*`). The administrator account is created on first start, and `CB_SERVER_URL` is wired to `W9_URL`.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 26.2, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 8978 |


### Data Directory


Data is persisted in the `cloudbeaver` volume, mounted at `/opt/cloudbeaver/workspace`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `W9_LOGIN_PASSWORD` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [CloudBeaver Administrator Guide](https://support.websoft9.com/docs/cloudbeaver) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/dbeaver/cloudbeaver)

- [GitHub docs](https://github.com/dbeaver/cloudbeaver/wiki/Server-configuration)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
