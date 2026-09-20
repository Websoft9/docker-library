# Databasus on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Databasus**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Databasus URL and create the first administrator account (email and password) on the sign-up screen.
2. Add a database connection, choose a storage destination, and create a backup job.
3. Run the first backup and check its status on the dashboard.

### Change Password

1. Sign in to Databasus and change the password from the user profile.
2. If you cannot sign in, reset it from the host:
   `docker exec -it databasus ./main --new-password="YourNewPassword" --email="admin"`.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Databasus Docker image](https://hub.docker.com/r/databasus/databasus) and makes some improvements below.

<!-- W9_NOTE_START -->
The package wires `DATABASUS_URL` to `W9_URL` so links Databasus generates use the public address. Optional SMTP, OAuth, telemetry, and logging settings are listed as comments at the end of `.env`.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: v3.57.1, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 4005 |


### Data Directory


Data is persisted in the `databasus-data` volume, mounted at `/databasus-data`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Databasus Administrator Guide](https://support.websoft9.com/docs/databasus) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/databasus/databasus)

- [Releases](https://github.com/databasus/databasus/releases)

- [Official docs](https://databasus.com/installation)

- [Official docs](https://databasus.com/advanced-config)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`; the first startup can take up to two minutes.

**First backup fails?**
- Ensure the target database accepts connections from the container and the credentials have the required dump privileges.

**Permission denied on the data volume?**
- Set `PUID` / `PGID` in `.env` to match the mount owner and rebuild the app.
<!-- W9_TROUBLESHOOT_END -->
