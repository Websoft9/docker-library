# Trivy on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Trivy**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

Trivy is deployed in server mode and exposes an HTTP API on port 4954.

1. Open `http://<host>:4954/healthz` and confirm it returns `ok`.
2. On a client machine, install the [Trivy CLI](https://trivy.dev/latest/docs/getting-started/installation/).
3. Run a scan against this server, for example `trivy image --server http://<host>:4954 --token <token> alpine:3.20`.

### Change Token

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update `W9_LOGIN_PASSWORD` (or `W9_POWER_PASSWORD`) in `.env` and save.
3. Rebuild the app; clients must use the new token.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Trivy Docker image](https://hub.docker.com/r/aquasec/trivy) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 0.74.0, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Trivy Server API | 4954 |


### Data Directory


Data is persisted in the `trivy_cache` volume, mounted at `/root/.cache/trivy`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Trivy Administrator Guide](https://support.websoft9.com/docs/trivy) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/aquasec/trivy)

- [Releases](https://github.com/aquasecurity/trivy/releases)

- [Official docs](https://trivy.dev/latest/docs/references/modes/client-server/)

- [Official docs](https://trivy.dev/latest/docs/references/configuration/cli/trivy_server/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
