# Airbyte on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Airbyte**.
2. In the **Access** tab, get the login URL and credentials.

3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Make sure you are signed in to the Airbyte admin console.
2. Try a core feature.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Airbyte Docker image](https://hub.docker.com/r/airbyte/server) and makes some improvements below.

<!-- W9_NOTE_START -->
This package uses a two-container k3s-in-Docker architecture (`airbyte` single-node k3s runtime + `airbyte-installer` one-shot Helm V2 installer) without relying on a host Docker socket:

- `W9_VERSION` tracks the Airbyte Helm chart version, while `AIRBYTE_K3S_IMAGE` controls the outer k3s runtime image independently.
- The installer exposes the Airbyte server service as a NodePort (`AIRBYTE_NODE_PORT`, default `30080`) inside k3s and maps the published host port to that NodePort.
- Initial bootstrap may take several minutes; treat the instance as ready after Helm deployment completes and `/api/v1/health` succeeds.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 2.2.0.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 30080 |


### Data Directory


- `kubeconfig` → `/shared`
- `k3s-data` → `/var/lib/rancher/k3s`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/installer/entrypoint.sh` to `/usr/local/bin/airbyte-installer.sh`.


## References

- [Airbyte Administrator Guide](https://support.websoft9.com/docs/airbyte) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/airbyte/server)

- [Releases](https://github.com/airbytehq/airbyte/releases)

- [Official docs](https://docs.airbyte.com/platform/deploying-airbyte)

- [Official docs](https://docs.airbyte.com/platform/deploying-airbyte/chart-v2-community)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
