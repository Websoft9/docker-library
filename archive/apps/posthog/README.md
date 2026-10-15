# PostHog on Docker

This app package deploys the official self-hosted PostHog stack on Websoft9 with Docker Compose.

- community: latest

## Requirements

PostHog recommends a VM roughly equivalent to:

- 4 vCPU
- 16 GB RAM
- 30 GB available disk

## Notes

- PostHog does not publish stable self-hosted releases in the usual `x.y.z` form.
- The upstream project recommends running the latest Docker image for self-hosted deployments.
- This package keeps the upstream multi-service topology instead of forcing a simplified Websoft9-style layout.
- Only the `proxy` entrypoint joins the shared `websoft9` network; internal services stay on the Compose-private network.
- This package exposes the PostHog web entrypoint through the internal Caddy proxy on port `80`.

## Install

Use the standard `docker-library` workflow for apps under `apps/posthog`.

## Upstream

- Docs: https://posthog.com/docs/self-host
- Source: https://github.com/PostHog/posthog
- Image: https://hub.docker.com/r/posthog/posthog
