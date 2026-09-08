# n8n on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **n8n**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the n8n admin console.
2. Try a core feature.

### Change Password

1. Sign in to the n8n web console.
2. Open your user settings and change the account password there.
3. For a locked-out instance, use n8n's owner-management or database recovery flow instead of changing `.env`.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [n8n Docker image](https://hub.docker.com/r/n8nio/n8n) and makes some improvements below.

<!-- W9_NOTE_START -->
This package keeps n8n's default single-container SQLite deployment and persists `/home/node/.n8n`, which stores the SQLite database, encryption key, and local runtime state.

For reverse-proxy deployments on a non-default public port, the package sets `N8N_EDITOR_BASE_URL`, `N8N_WEBHOOK_URL`, and `N8N_PROXY_HOPS=1` so the UI and webhook URLs use the external address instead of the internal container port.

Timezone is configured directly from environment variables with `GENERIC_TIMEZONE` and `TZ`; this package no longer relies on the deprecated `N8N_CONFIG_FILES` startup path.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 2.38.4, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 5678 |


### Data Directory


Data is persisted in the `n8n` volume, mounted at `/home/node/.n8n`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [n8n Administrator Guide](https://support.websoft9.com/docs/n8n) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/n8nio/n8n)

- [Releases](https://github.com/n8n-io/n8n/releases/tag/n8n%402.38.4)

- [Official docs](https://docs.n8n.io/deploy/host-n8n/install-options/install-with-docker.md)

- [Official docs](https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/use-environment-variables/deployment.md)

- [Official docs](https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/configuration-examples/configure-webhook-urls-with-reverse-proxy.md)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
