# Semaphore UI on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Semaphore UI**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Semaphore UI admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Semaphore UI Docker image](https://hub.docker.com/r/semaphoreui/semaphore) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: v2.19.16, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 3000 |


### Data Directory


- `semaphore` → `/var/lib/semaphore`
- `mysql` → `/var/lib/mysql`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `SEMAPHORE_ADMIN`, `SEMAPHORE_ADMIN_NAME`, `SEMAPHORE_ADMIN_EMAIL`, `SEMAPHORE_ADMIN_PASSWORD` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Semaphore UI Administrator Guide](https://support.websoft9.com/docs/semaphoreui) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/semaphoreui/semaphore)

- [Releases](https://github.com/semaphoreui/semaphore/releases)

- [Official docs](https://docs.semaphoreui.com/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
