# Umbraco on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Umbraco**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open `https://<host>:${W9_HTTPS_PORT_SET}` from the **Access** tab and accept the self-signed certificate warning.
2. Sign in to the backoffice at `/umbraco` with the credentials from the **Access** tab.
3. Create your first content node to confirm the publishing flow.

### Change Password

1. Change the administrator password from the user profile inside the Umbraco backoffice.
2. `W9_LOGIN_USER` and `W9_LOGIN_PASSWORD` create the administrator on first start only; changing them afterwards requires updating the user in the backoffice or removing the `umbraco_data` volume and rebuilding.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Umbraco Docker image](https://hub.docker.com/r/websoft9dev/umbraco) and makes some improvements below.

<!-- W9_NOTE_START -->

- Umbraco runs HTTPS by default with a self-signed certificate generated on first start and stored in the `umbraco_data` volume.
- Application logs are written to both `docker logs` and the persisted Umbraco log files under `/app/umbraco/Logs`.

<!-- W9_NOTE_END -->

`docker compose up` uses the prebuilt image `${W9_REPO}:${W9_VERSION}`. The local `Dockerfile` is kept for separate image build/publish workflows and is not invoked by the runtime compose file.

Apps run as containers; recreate after any configuration change.

### Version Support

Supported versions: 18.2.0.


### Ports

| Purpose | Port |
| --- | --- |
| HTTPS | 8443 |


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

**Certificate warning in the browser?**
- The package serves a self-signed certificate by default. Open `https://<host>:${W9_HTTPS_PORT_SET}` and accept the warning, or replace it with your own certificate at the reverse proxy layer.

**Port not reachable?**
- Ensure the firewall / security group allows the HTTPS port.
<!-- W9_TROUBLESHOOT_END -->
