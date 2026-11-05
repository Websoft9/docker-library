# ThingsBoard on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **ThingsBoard**.
2. In the **Access** tab, get the login URL and credentials.

   No preset administrator credentials are shipped; create the admin account in the setup wizard.

3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. On first launch, complete the setup wizard and create the system administrator account.
2. Select the option to load demo data if you want sample tenants, devices, and dashboards.
3. Sign in with the account you created.

### Change Password

1. Sign in to the ThingsBoard web UI.
2. Open the account menu in the top-right corner, choose **Account**, and change the password.
3. Administrators can reset other users' passwords under **Users**.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [ThingsBoard Docker image](https://hub.docker.com/r/thingsboard/tb-node) and makes some improvements below.

<!-- W9_NOTE_START -->
ThingsBoard 4.4 requires a license for production use. This package defaults to non-production mode, which is watermarked and shuts down after 30 cumulative days. For production, set `TB_LICENSE_SECRET` in `.env` to your license key; a valid key takes precedence over non-production mode. The first launch requires creating the system administrator in the setup wizard; no default login is provided. See the [Community Grant Program](https://thingsboard.io/community-grant-program/).
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Initialization

Run `docker compose up -d` once for a new installation. A short startup script runs the official installer, writes `/data/.tb-installed` only after success, and starts ThingsBoard. Subsequent starts skip installation when this marker exists. There is no separate init service, SQL inspection or Java guard. Demo data is selected in the setup wizard, not loaded by the installer.

An interrupted or failed installation leaves `/data/.tb-installing`, preventing automatic retries. Review `docker compose logs thingsboard-ce`; repair or restore the database before removing this directory to allow another attempt. Do not delete populated databases or mark incomplete installations as successful. The marker tracks installation only; it does not validate the database or perform upgrades.

An existing database without a marker is not detected automatically. Before starting this package, confirm that the database is fully installed and matches the configured connection, then create its marker:

```bash
docker compose run --rm --no-deps --entrypoint bash thingsboard-ce -ec 'touch /data/.tb-installed'
```

Back up and restore the database and `license-data` volume together. Do not reuse a marker with a different or empty database; changing the datasource requires reviewing the marker as well.

The official `tb-web-report` service is included on the internal network; it has no published host port.

### Version Support

Supported versions: 4.4.0-latest, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 8080 |

Only the Web Console is published by default. Device protocol ports are not exposed automatically; add only the mappings required by your deployment.

### Data Directory


Database data is persisted in the existing `postgres-data` volume at `/var/lib/postgresql`. The official `license-data` volume is mounted at `/data` and stores both license data and installation markers. No extra state volume is needed; markers do not replace database backups.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [ThingsBoard Administrator Guide](https://support.websoft9.com/docs/thingsboard) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/thingsboard/tb-node)

- [Releases](https://github.com/thingsboard/thingsboard/releases)

- [Official docs](https://thingsboard.io/docs/installation/docker/)

- [ThingsBoard 4.4 installation and setup](https://thingsboard.io/docs/pe/installation/docker/)

- [GitHub docs](https://github.com/thingsboard/thingsboard)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
