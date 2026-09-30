# MongoDB on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **MongoDB**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the MongoDB admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [MongoDB Docker image](https://hub.docker.com/_/mongo) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 8.3, 8.0, 7.0, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| MongoDB | 27017 |


### Data Directory


Data is persisted in the `mongo_data` volume, mounted at `/data/db`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration is overridden by mounting `./src/mongod.conf` to `/etc/mongod.conf`.


## References

- [MongoDB Administrator Guide](https://support.websoft9.com/docs/mongodb) by Websoft9

- [Docker Hub image](https://hub.docker.com/_/mongo)

- [GitHub docs](https://github.com/docker-library/mongo)

- [Official docs](https://www.mongodb.com/docs/manual/installation/)

- [Official docs](https://www.mongodb.com/docs/manual/reference/versioning/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
