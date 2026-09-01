# AFFiNE on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **AFFiNE**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the AFFiNE admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [AFFiNE Docker image](https://ghcr.io/toeverything/affine) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 0.27.4, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 3010 |


### Data Directory


- `affine_storage` → `/root/.affine/storage`
- `affine_postgres` → `/var/lib/postgresql/data`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/config.json` to `/root/.affine/config/config.json`.


## References

- [AFFiNE Administrator Guide](https://support.websoft9.com/docs/affine) by Websoft9

- [GHCR image](https://ghcr.io/toeverything/affine)

- [Releases](https://github.com/toeverything/AFFiNE)

- [Official compose](https://github.com/toeverything/AFFiNE/releases/latest/download/docker-compose.yml)

- [Official env example](https://github.com/toeverything/AFFiNE/releases/latest/download/config.json.example)

- [Official docs](https://docs.affine.pro/self-host-affine/install/docker-compose-recommended)

- [Official docs](https://docs.affine.pro/self-host-affine/install/configuration)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
