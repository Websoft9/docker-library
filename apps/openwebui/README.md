# Open WebUI on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Open WebUI**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open `http://<host>:9001` and create the first account; the first sign-up becomes the administrator.
2. Go to **Settings > Admin Settings** to add an LLM provider.
3. Select a model and start chatting.

### Optional local AI

`ollama` and `chroma` are optional profiles and are not started by default:

- `docker compose --profile ollama up -d` starts a local Ollama runtime; pull a model with `docker exec <app>-ollama ollama pull <model>`.
- `docker compose --profile chroma up -d` starts an external Chroma vector database; then set `CHROMA_HTTP_HOST=${W9_ID}-chroma` and `CHROMA_HTTP_PORT=8000` in `.env` and rebuild.

### Change Password

Open WebUI manages accounts in the app, not in `.env`. Sign in, open **Settings > Account**, and change the password there. To reset the administrator password, use the Open WebUI admin panel or the database.

### GPU / CUDA

Open WebUI also publishes CUDA image tags (for example `cuda` and `v0.11.3-cuda`) for NVIDIA GPU hosts. This package does not use the CUDA variant; GPU support is out of scope here.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Open WebUI Docker image](https://ghcr.io/open-webui/open-webui) and makes some improvements below.

<!-- W9_NOTE_START -->
The image tag is pinned to `0.11`. `main` is offered only as a rolling test option and is not guaranteed to be stable.

`ollama` and `chroma` are optional Docker Compose profiles: they are not started by default and publish no host ports. The CUDA image variant exists upstream but is out of scope for this package.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 0.11, main.


### Ports

| Purpose | Port |
| --- | --- |
| Web UI | 8080 |


### Data Directory


- `open-webui` → `/app/backend/data`
- `ollama` → `/root/.ollama`
- `chroma` → `/data`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Open WebUI Administrator Guide](https://support.websoft9.com/docs/openwebui) by Websoft9

- [GHCR image](https://ghcr.io/open-webui/open-webui)

- [Releases](https://github.com/open-webui/open-webui/releases)

- [Official docs](https://docs.openwebui.com/)

- [Official docs](https://docs.openwebui.com/getting-started/quick-start/)

- [Official docs](https://docs.openwebui.com/reference/env-configuration/)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.

**Local model not available?**
- Start the optional Ollama profile with `docker compose --profile ollama up -d`, then pull a model inside the container.
<!-- W9_TROUBLESHOOT_END -->
