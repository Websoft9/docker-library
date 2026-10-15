# Xinference on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Xinference**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

Xinference exposes an OpenAI-compatible RESTful API and a Web UI. Authentication is enabled by default since v3.0, so the first visit to the Web UI opens a setup page where you create the initial administrator account.

1. Open the app URL and complete the first-run setup to create the administrator account.
2. Sign in and use **Launch Model** to download and start a model; the first launch of a model installs its engine dependencies and takes longer.

### Change Password

Use the Web UI **User Management** page, or reset it from a shell with:

```bash
docker exec -it xinference xinference-reset-auth-password --username admin
```
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Xinference Docker image](https://hub.docker.com/r/xprobe/xinference) and makes some improvements below.

<!-- W9_NOTE_START -->
The package does not preset credentials: the first visit to the Web UI creates the initial administrator account.

The package ships the GPU image variant (`xprobe/xinference:v4.0.0`) and reserves all NVIDIA GPUs, so the host must have an NVIDIA GPU with CUDA 13.0 and driver 580+. On a CPU-only host, set `W9_VERSION=v4.0.0-cpu` in `.env` and remove the `deploy.resources.reservations.devices` block from `docker-compose.yml`.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: v4.0.0, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web UI / API | 9997 |


### Data Directory


- `xinference_home` → `/root/.xinference`
- `huggingface_cache` → `/root/.cache/huggingface`
- `modelscope_cache` → `/root/.cache/modelscope`



### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Xinference Administrator Guide](https://support.websoft9.com/docs/xinference) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/xprobe/xinference)

- [Releases](https://github.com/xorbitsai/inference)

- [Official compose](https://raw.githubusercontent.com/xorbitsai/inference/main/xinference/deploy/docker/docker-compose.yml)

- [Official env example](https://raw.githubusercontent.com/xorbitsai/inference/main/xinference/deploy/docker/.env.example)

- [Official docs](https://inference.readthedocs.io/en/latest/getting_started/installation.html)

- [Official docs](https://inference.readthedocs.io/en/latest/getting_started/using_docker_image.html)

- [Official docs](https://inference.readthedocs.io/en/latest/getting_started/using_docker_compose.html)

- [Official docs](https://inference.readthedocs.io/en/latest/user_guide/auth_system.html)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**Web UI asks for account setup on first visit?**
- This is expected: create the initial administrator account in the browser.

**Model launch is slow the first time?**
- Xinference installs the engine dependencies into a per-model virtual environment on first launch; later launches reuse it.

**Not enough memory to load a model?**
- Raise the container memory limit and choose a smaller model or quantization.
<!-- W9_TROUBLESHOOT_END -->
