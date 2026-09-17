# Hermes Agent on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Hermes Agent**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the dashboard URL from the **Access** tab and sign in with the basic-auth credentials (`W9_LOGIN_USER` / `W9_LOGIN_PASSWORD`).
2. Add an LLM provider key (for example `OPENROUTER_API_KEY`) in the app's **Compose** tab `.env`, save, and rebuild.
3. In the dashboard, pick a model and start a conversation. The OpenAI-compatible API is served on the API port and authenticated with the `W9_POWER_PASSWORD` bearer key.

### Change Password

1. In the [Websoft9](https://www.websoft9.com) console, open the app's **Compose** tab.
2. Update `W9_POWER_PASSWORD` in `.env` and save; this drives both the dashboard password and the API bearer key.
3. Rebuild the app.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Hermes Agent Docker image](https://hub.docker.com/r/nousresearch/hermes-agent) and makes some improvements below.

<!-- W9_NOTE_START -->
Hermes Agent is an autonomous, self-improving AI agent. This package runs it as a persistent gateway with a supervised web dashboard on port 9119 and an OpenAI-compatible API server on port 8642.

The container stores all state (configuration, `.env`, sessions, memories, skills, and logs) in a single directory mounted from the `hermes_agent_data` volume at `/opt/data`. The image itself is stateless, so upgrading means changing `W9_VERSION` and recreating the container; the mounted data is preserved.

The dashboard binds `0.0.0.0:9119` and fails closed without an authentication provider, so the package seeds dashboard basic auth from `W9_LOGIN_USER` / `W9_LOGIN_PASSWORD`. `HERMES_DASHBOARD_BASIC_AUTH_SECRET` must be at least 16 bytes, which is why `W9_POWER_PASSWORD` is at least 16 characters.

The agent needs an LLM provider. Add a key such as `OPENROUTER_API_KEY` to `.env` (the variable is commented out by default) and recreate the container. The OpenAI-compatible API server on `8642` only starts once a provider key is configured and is authenticated with the `W9_POWER_PASSWORD` bearer key. Additional messaging platforms (Telegram, Discord, Slack, and more) are configured through the dashboard or their own environment variables.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: v2026.9.14, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Dashboard | 9119 |
| OpenAI-compatible API server | 8642 |


### Data Directory


Data is persisted in the `hermes_data` volume, mounted at `/opt/data`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Hermes Agent Administrator Guide](https://support.websoft9.com/docs/hermes) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/nousresearch/hermes-agent)

- [Releases](https://github.com/NousResearch/hermes-agent)

- [Official compose](https://raw.githubusercontent.com/NousResearch/hermes-agent/main/docker-compose.yml)

- [Official env example](https://raw.githubusercontent.com/NousResearch/hermes-agent/main/.env.example)

- [GitHub docs](https://github.com/NousResearch/hermes-agent)

- [Official docs](https://hermes-agent.nousresearch.com/docs/user-guide/docker)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**The first start is slow?**
- The image is 5 GB+ and the first pull can take several minutes.

**Dashboard does not open?**
- The dashboard needs an auth provider; keep `HERMES_DASHBOARD_BASIC_AUTH_*` set, make sure `W9_POWER_PASSWORD` is at least 16 characters, and wait for the health check to pass.

**The API port is closed?**
- The API server only starts after an LLM provider key is configured. Add one (for example `OPENROUTER_API_KEY`) to `.env` and recreate the container.

**The agent replies with a provider error?**
- No LLM provider key is configured. Add one (for example `OPENROUTER_API_KEY`) to `.env` and rebuild.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
