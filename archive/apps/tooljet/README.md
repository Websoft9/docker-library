# ToolJet on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **ToolJet**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the app URL and complete the first-run administrator signup.
2. Create a workspace, then build an app from the ToolJet dashboard.
3. Connect a data source and run a query to confirm the app works.

### Change Password

1. Sign in to ToolJet and update the password from the account settings.
2. ToolJet stores users in its own database; changing `.env` does not change an existing account password.
3. Keep `LOCKBOX_MASTER_KEY` and `SECRET_KEY_BASE` unchanged after first startup, or existing encrypted data can no longer be decrypted.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [ToolJet Docker image](https://hub.docker.com/r/tooljet/tooljet-ce) and makes some improvements below.

<!-- W9_NOTE_START -->
The package bundles PostgreSQL 13, Redis, and PostgREST for a single-node deployment. `LOCKBOX_MASTER_KEY` and `SECRET_KEY_BASE` are generated from the package seed and must stay unchanged after first startup, or existing encrypted data can no longer be decrypted.

It also ships `src/nginx-proxy.conf`, which the Websoft9 Gateway reads and injects into the Proxy Host `server{}` block to apply the proxy buffering and platform client rate/concurrency limits. It is not mounted into the container and is unrelated to `docker-compose.yml`.

### ToolJet MCP

ToolJet provides an official MCP server so AI coding agents can build apps in your workspace. It runs on your machine, not in this container.

1. In ToolJet, open **Profile Settings → Personal access tokens** and create a token (`tj_pat_...`).
2. Install the server in your AI client (Codex / Claude Code / VS Code Copilot): https://github.com/ToolJet/tooljet-mcp
3. Point it at this instance:

   ```
   TOOLJET_DEPLOYMENT_URL=https://<your-domain>
   TOOLJET_PAT=tj_pat_...
   ```

Docs: https://docs.tooljet.com/docs/build-with-ai/mcp/setup/
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: v3.20.226-lts, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 80 |


### Data Directory


- `postgres` → `/var/lib/postgresql/data`
- `redis_data` → `/var/lib/redis/data`
- `backup` → `/backup`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [ToolJet Administrator Guide](https://support.websoft9.com/docs/tooljet) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/tooljet/tooljet-ce)

- [GitHub docs](https://github.com/ToolJet/ToolJet)

- [Official docs](https://docs.tooljet.com/docs/setup/docker/)

- [Official docs](https://docs.tooljet.com/docs/setup/env-vars)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
