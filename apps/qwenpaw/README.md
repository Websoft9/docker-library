# QwenPaw on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **QwenPaw**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Hub URL from the **Access** tab and sign in with the packaged administrator account.
2. Go to **User Management** to create accounts, or let members register themselves (registration is `open` by default).
3. Each member signs in and gets a personal, isolated QwenPaw runtime.
4. In a personal Console, open **Settings → Models** to add a provider and API key or to select a local model.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update the password in `.env` and save.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [QwenPaw Docker image](https://hub.docker.com/r/agentscope/qwenpaw) and makes some improvements below.

<!-- W9_NOTE_START -->
- This package runs **QwenPaw Hub**, the multi-user control plane, directly from the official `agentscope/qwenpaw` image. One web address serves an administrator and many per-user QwenPaw runtimes, each with separate workspaces, credentials, and conversations.
- The Hub console listens on port `8000` inside the container and is published through `W9_HTTP_PORT_SET`. `QWENPAW_HUB_PUBLIC_BASE_URL` is derived from `W9_URL` and must match the address users open in their browsers.
- The official image is the single-user Console image, so the container installs the Hub control-plane `docker` SDK and `bubblewrap` on startup when they are missing. The Local runtime backend therefore requires `privileged: true`. The first start needs network access and takes longer while these packages install.
- The first administrator is seeded from `W9_LOGIN_USER` / `W9_LOGIN_PASSWORD` on first startup only. Set `QWENPAW_HUB_REGISTRATION_MODE` (`open`, `invite`, or `closed`) to control self-registration; use `closed` and create accounts in **User Management** for a locked-down deployment.
- The upstream project marks Hub as an early release intended for trusted teams only, not for mutually untrusted users.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| QwenPaw Hub console | 8000 |


### Data Directory


Data is persisted in the `qwenpaw_data` volume, mounted at `/app/working`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


Note: `QWENPAW_HUB_ADMIN_USER`, `QWENPAW_HUB_ADMIN_PASSWORD` take effect on first startup only; changing them after deployment may not take effect until the app is re-initialized.


### Configuration Files


Configuration is overridden by mounting `./src/hub-entrypoint.sh` to `/opt/qwenpaw/hub-entrypoint.sh`.


## References

- [QwenPaw Administrator Guide](https://support.websoft9.com/docs/qwenpaw) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/agentscope/qwenpaw)

- [Releases](https://github.com/agentscope-ai/QwenPaw/releases)

- [Official compose](https://raw.githubusercontent.com/agentscope-ai/QwenPaw/main/docker-compose.yml)

- [Official env example](https://qwenpaw.agentscope.io/docs/config)

- [GitHub docs](https://github.com/agentscope-ai/QwenPaw)

- [Official docs](https://qwenpaw.agentscope.io/docs/quickstart)

- [Official docs](https://qwenpaw.agentscope.io/docs/hub)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App takes long on first start?**
- The container installs the Hub `docker` SDK and `bubblewrap` on first start; allow a few minutes and check `docker compose logs`.

**App fails to start?**
- Check `docker compose logs`.

**Cannot create or start a user runtime?**
- Confirm the container is running as privileged (needed for bubblewrap) and check the Hub **Runtimes** page for the latest error.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
