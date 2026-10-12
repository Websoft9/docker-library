# LiteLLM on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **LiteLLM**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

1. Open `/ui` to manage the proxy and inspect configured models.
2. Set at least one provider key such as `OPENAI_API_KEY` in `.env`, then rebuild.
3. Send an OpenAI-compatible request to `/v1/chat/completions`.

### Change Password

1. The Admin UI uses `UI_USERNAME` and `UI_PASSWORD` from `.env`.
2. The API and proxy admin key use `LITELLM_MASTER_KEY`.
3. Do not rotate `LITELLM_SALT_KEY` after first deployment unless you also reset encrypted credentials in the database.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [LiteLLM Docker image](https://ghcr.io/berriai/litellm) and makes some improvements below.

<!-- W9_NOTE_START -->
This package follows LiteLLM's official DB-backed quickstart topology so the `/ui` admin console, model catalog, and key management are available. The package also sets `UI_USERNAME` and `UI_PASSWORD`, so the Admin UI no longer falls back to using `LITELLM_MASTER_KEY` as the login password.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: v1.105.0.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 4000 |


### Data Directory


Data is persisted in the `postgres_data` volume, mounted at `/var/lib/postgresql/data`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration is overridden by mounting `./src/proxy_server_config.yaml` to `/app/proxy_server_config.yaml`.


## References

- [LiteLLM Administrator Guide](https://support.websoft9.com/docs/litellm) by Websoft9

- [GHCR image](https://ghcr.io/berriai/litellm)

- [Releases](https://github.com/BerriAI/litellm/releases)

- [Official docs](https://docs.litellm.ai/docs/proxy/docker_quick_start)

- [Official docs](https://docs.litellm.ai/docs/proxy/quick_start)

- [GitHub docs](https://github.com/BerriAI/litellm)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
