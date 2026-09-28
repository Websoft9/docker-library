# Vault on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Vault**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Vault URL from the Websoft9 **Access** tab; the web UI and HTTP API are served on port 8200.
2. Get the root token from the container logs: run `docker logs vault` and look for the `Root Token:` line.
3. Paste the token into the Vault sign-in page.

### Change Token

This package runs Vault in dev mode, so all data is held in memory and a new root token is generated on every restart. To use a fixed token, set `VAULT_DEV_ROOT_TOKEN_ID` in `.env` and rebuild.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Vault Docker image](https://hub.docker.com/r/hashicorp/vault) and makes some improvements below.

<!-- W9_NOTE_START -->
This package runs Vault in dev mode (`server -dev`): storage is in memory and the root token is printed in the container logs. Do not use it for production data.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 2.1, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Vault UI and HTTP API | 8200 |


### Data Directory


- `vault-logs` → `/vault/logs`
- `vault-file` → `/vault/file`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Vault Administrator Guide](https://support.websoft9.com/docs/vault) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/hashicorp/vault)

- [Releases](https://github.com/hashicorp/vault/releases)

- [Official docs](https://developer.hashicorp.com/vault/docs)

- [Official docs](https://hub.docker.com/r/hashicorp/vault)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
