# Umbraco on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Umbraco**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Umbraco site from the **Access** tab.
2. Sign in to the backoffice at `/umbraco` with the credentials from the **Access** tab.
3. Create your first content node to confirm the publishing flow.

### Change Password

1. Change the administrator password from the user profile inside the Umbraco backoffice.
2. `W9_LOGIN_USER` and `W9_LOGIN_PASSWORD` create the administrator on first start only; changing them afterwards requires updating the user in the backoffice or removing the `umbraco_data` volume and rebuilding.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Umbraco Docker image](https://hub.docker.com/r/websoft9dev/umbraco) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 18.2.0.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 8080 |


### Data Directory


- `umbraco_data` → `/app/umbraco`
- `umbraco_media` → `/app/wwwroot/media`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `W9_LOGIN_USER`, `W9_LOGIN_PASSWORD` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Umbraco Administrator Guide](https://support.websoft9.com/docs/umbraco) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/websoft9dev/umbraco)

- [Releases](https://github.com/umbraco/Umbraco-CMS/releases)

- [Official docs](https://docs.umbraco.com/umbraco-cms/get-started/installation/running-umbraco-on-docker-locally)

- [Official docs](https://docs.umbraco.com/umbraco-cms/run-in-production/infrastructure-and-ops/server-setup/running-umbraco-in-docker)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
