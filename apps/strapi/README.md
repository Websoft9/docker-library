# Strapi on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Strapi**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Strapi admin console from the **Access** tab.
2. Sign in with the initial administrator account.
3. Create a content type or a test entry to confirm the CMS is writable.

### Change Password

1. Change the administrator password from the profile menu inside the Strapi admin console.
2. `W9_LOGIN_USER` and `W9_LOGIN_PASSWORD` create the first administrator on first start only; changing them later requires using the Strapi CLI or removing the persisted data volume and rebuilding.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Strapi Docker image](https://github.com/strapi/strapi) and makes some improvements below.

<!-- W9_NOTE_START -->
### Package Notes

- Strapi 5 no longer publishes official container images, so Websoft9 provides and consumes a prebuilt `websoft9dev/strapi` image for this package.
- The bundled SQLite database is stored in the `strapi_data` volume.
- The first administrator is created automatically on first start from `W9_LOGIN_USER` and `W9_LOGIN_PASSWORD`.
- An external PostgreSQL or MySQL database can be used instead of the bundled SQLite by setting `DATABASE_CLIENT` and the `DATABASE_*` connection variables in `.env`. The external database must be empty on first start; existing SQLite data is not migrated automatically.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 5.54.0, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 1337 |


### Data Directory


- `strapi_data` → `/opt/app/.tmp`
- `strapi_uploads` → `/opt/app/public/uploads`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `W9_LOGIN_USER`, `W9_LOGIN_PASSWORD` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Strapi Administrator Guide](https://support.websoft9.com/docs/strapi) by Websoft9

- [Docker Hub image](https://github.com/strapi/strapi)

- [Releases](https://github.com/strapi/strapi/releases)

- [Official docs](https://docs.strapi.io/cms/installation/docker)

- [Official docs](https://docs.strapi.io/cms/configurations/environment)

- [Official docs](https://docs.strapi.io/cms/migration/v4-to-v5/introduction-and-faq)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Admin page not reachable?**
- Confirm the published port is open and the container healthcheck reaches `/_health`.
<!-- W9_TROUBLESHOOT_END -->
