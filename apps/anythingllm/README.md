# AnythingLLM on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **AnythingLLM**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

AnythingLLM is a private AI chat console where you talk with your own documents and workspaces. On first run it opens a setup wizard:

1. In the setup wizard choose a model provider — an online provider such as OpenAI or Anthropic, or a local Ollama instance — and enter its API key.
2. Create or open a workspace, then upload documents to it so the assistant can answer from your own content.
3. Start a chat and ask a question; verify the answer is grounded in the documents you added.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [AnythingLLM Docker image](https://hub.docker.com/r/mintplexlabs/anythingllm) and makes some improvements below.

<!-- W9_NOTE_START -->

<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 1.16, latest.

The `latest` tag is not guaranteed to remain valid; pin a specific version for production.


### Ports

| Purpose | Port |
| --- | --- |
| Web Console | 3001 |


### Data Directory


Data is persisted in the `anythingllm` volume, mounted at `/app/server/storage`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [AnythingLLM Administrator Guide](https://support.websoft9.com/docs/anythingllm) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/mintplexlabs/anythingllm)

- [Releases](https://github.com/Mintplex-Labs/anything-llm)

- [Official compose](https://github.com/Mintplex-Labs/anything-llm/blob/master/docker/docker-compose.yml)

- [Official env example](https://github.com/Mintplex-Labs/anything-llm/blob/master/docker/.env.example)

- [GitHub docs](https://github.com/Mintplex-Labs/anything-llm)

- [Official docs](https://docs.anythingllm.com/installation-docker/local-docker)

- [GitHub docs](https://github.com/Mintplex-Labs/anything-llm/blob/master/docker/HOW_TO_USE_DOCKER.md)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**App fails to start?**
- Check `docker compose logs`.

**Port not reachable?**
- Ensure the firewall / security group allows the port.
<!-- W9_TROUBLESHOOT_END -->
