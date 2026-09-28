# DeepSeek Harness on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **DeepSeek Harness**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open the Web UI from the **Access** tab.
2. Add `/workspace` as the initial workspace directory.
3. Configure a model provider in **Settings -> Models** before starting agent tasks.
4. Set `W9_URL` to the real external hostname you use to open the app, otherwise DSH may reject browser API calls with HTTP 403.
5. `DSH_TRUSTED_HOSTS` defaults to `${W9_URL}`. If the app is reachable by more than one browser authority, extend it as a comma-separated list.
6. Fill `W9_DEEPSEEK_API_KEY_SET` during installation if you want the built-in DeepSeek provider to work immediately after the first boot.
7. This package enables `DSH_FORCE_LOOPBACK_UI=true` by default so the public Websoft9 URL can open the Models/settings pages without requiring an SSH tunnel.

### First Access

1. DeepSeek Harness prints a one-time login URL with a `token=` query parameter in the container logs on startup.
2. If the root page returns `401 Unauthorized`, open the container logs and copy the latest `dsh web: http://127.0.0.1:3081/?token=...` URL suffix.
3. Replace `http://127.0.0.1:3081` with your Websoft9 access URL, then open that URL in the browser.

### Loopback Management Workaround

1. DeepSeek Harness currently keeps some Host-backed settings unavailable on non-loopback browser pages by design.
2. If you need the full **Settings -> Models** experience, create an SSH tunnel to the server and open the Web UI through a loopback address.
3. Example:

```bash
ssh -N -L 3081:127.0.0.1:3081 root@YOUR_SERVER_IP
```

4. Then open `http://127.0.0.1:3081/?token=...` with the latest token printed in the container logs.
5. This workaround is mainly needed for Host-persisted settings such as provider/model configuration; ordinary chat and agent sessions can still run through the normal published Websoft9 URL.

### Safety Notes

1. DeepSeek Harness is developer-preview software and should be run with the least privileges possible.
2. Do not mount sensitive host paths or credentials into `/workspace` unless you accept the risk.
3. Review provider keys, plugins, and model-generated commands before allowing broad access.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [DeepSeek Harness Docker image](https://www.npmjs.com/package/@deepseek-ai/dsh) and makes some improvements below.

<!-- W9_NOTE_START -->
### Package Notes

- This package builds a local image because upstream currently distributes DeepSeek Harness primarily as a Node/npm application instead of an official container image.
- The Web UI listens on port 3080 and stores persistent state in `/var/lib/dsh`.
- The default workspace path inside the container is `/workspace` and is backed by a dedicated named volume.
- This package exposes `W9_DEEPSEEK_API_KEY_SET` as the install-time input and maps it to the container's `DEEPSEEK_API_KEY` environment variable.
- Upstream marks DeepSeek Harness as experimental developer-preview software that has not completed a security audit.
- The first browser login is token-based; the current token can be read from the container logs.
- `W9_URL` is used as the trusted browser host for DSH's Host/Origin security checks and should match the real access domain or host:port.
- `DSH_TRUSTED_HOSTS` can add extra allowed browser authorities when the app is accessed through multiple domains, IPs, or forwarded ports.
- `DEEPSEEK_BASE_URL` is unrelated to browser access. It overrides the outbound LLM API endpoint used when DSH talks to a DeepSeek-compatible model provider.
- This package patches the installed DSH web client so `DSH_FORCE_LOOPBACK_UI=true` treats the public browser page like a loopback management surface, enabling Host-backed settings such as Models/provider configuration.
- Runtime deployment consumes the prebuilt `${W9_REPO}:${W9_VERSION}` image; the local `Dockerfile` is kept for repository-controlled image builds, not for `docker compose up` on the target host.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 0.1.7-rc.2, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 3080 |


### Data Directory


Data is kept inside the container; a named volume is recommended for persistence.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [DeepSeek Harness Administrator Guide](https://support.websoft9.com/docs/dsh) by Websoft9

- [Docker Hub image](https://www.npmjs.com/package/@deepseek-ai/dsh)

- [Releases](https://github.com/deepseek-ai/deepseek-harness/releases)

- [GitHub docs](https://github.com/deepseek-ai/deepseek-harness)

- [Official docs](https://deepseek-harness.github.io/deepseek-harness/en/guide/quickstart)

- [Official docs](https://raw.githubusercontent.com/deepseek-ai/deepseek-harness/master/SAFETY.md)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.

**Root page returns 401 Unauthorized?**
- Copy the latest `token=` login URL from `docker compose logs dsh` and open it through the published Websoft9 URL.

**UI keeps showing Connecting or `/api/...` returns 403?**
- Set `W9_URL` to the exact external hostname or `host:port` used by the browser, then redeploy so DSH trusts that Host/Origin.
- If you use more than one access address, add all of them to `DSH_TRUSTED_HOSTS` and redeploy.

**Models page says no API key for `deepseek-official`?**
- Fill `W9_DEEPSEEK_API_KEY_SET` and redeploy, or enter the key later through **Settings -> Models** when the current upstream build allows the onboarding flow.

**Settings page says `settings are unavailable in this browser` or `加载提供商目录失败`?**
- This package enables a compatibility patch by default with `DSH_FORCE_LOOPBACK_UI=true`, so the public Websoft9 URL should be able to open Host-backed settings such as the Models/provider directory.
- If you explicitly disabled that patch, re-enable `DSH_FORCE_LOOPBACK_UI=true` and redeploy, or use loopback access through an SSH tunnel.
<!-- W9_TROUBLESHOOT_END -->
