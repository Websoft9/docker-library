[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![GitHub last commit](https://img.shields.io/github/last-commit/Websoft9/docker-library)](https://github.com/Websoft9/docker-library)
[![GitHub Release Date](https://img.shields.io/github/release-date/Websoft9/docker-library)](https://github.com/Websoft9/docker-library)

# Websoft9 Docker Library

This repository is the template library behind the [Websoft9 App Store](https://www.websoft9.com/apps). It contains [100+ application packages](apps/) built on [Docker Compose](https://docs.docker.com/compose/), such as WordPress, MySQL, Odoo, MongoDB, GitLab, Grafana, n8n, Nextcloud, and ONLYOFFICE.

Each directory under `apps/` is one independent deployment unit: a complete, versioned package that can be started with `docker compose up`, or deployed through the Websoft9 console.

Core design goals:

- one app directory = one deployable unit
- every app runs with `docker compose up`
- consistent environment, network, and file conventions
- machine-readable metadata for the Websoft9 platform and AI agents
- repeatable, auditable maintenance

## AI-driven maintenance

This repository is maintained by AI agents under owner review. The owner decides demand and the final end-to-end result; AI handles upstream research, implementation, routine validation, and reporting.

Entry points for contributors and agents:

- `AGENTS.md` - repository rules and fastest entry point
- `docs/ai-sdlc/` - AI delivery pipeline, quality gates, and report format
- `skills/` - shared agent workflows for new apps, updates, deployment validation, and archive/restore
- `metadata/maintenance.yaml` and `metadata/archive.yaml` - maintenance and lifecycle state
- `cli/` - the `libs` automation interface

## Quick start

1. Install Docker.

   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
   sudo systemctl enable --now docker
   ```

2. Clone this repository and list the available apps.

   ```bash
   git clone --depth=1 https://github.com/Websoft9/docker-library.git
   cd docker-library && ls apps
   ```

3. Enter an app directory, review `.env` (at minimum set `W9_POWER_PASSWORD`), and start it.

   ```bash
   docker network create websoft9
   cd apps/wordpress
   sudo docker compose up -d
   ```

The Websoft9 console is the easiest way to run these packages with a web UI, domains, HTTPS, backups, and lifecycle management.

## AI agent commands (opencode)

| Command | Purpose |
|---|---|
| `/libs-new-app <app> <trademark> <reference URL>` | Create a new app package |
| `/libs-update-assessment <app>` | Check upstream versions and decide whether an update is worth doing |
| `/libs-update-app <app> [version]` | Implement an approved update and produce a report |
| `/libs-batch-update-app <selector>` | Update a batch of apps by name list or initials |
| `/libs-deploy-validation <app> [local]` | Prove an app deploys and passes structure, policy, reachability, and log checks |
| `/libs-release-readiness <app>` | Check whether a task is ready for owner E2E or release |
| `/libs-test-report <app> <evidence source>` | Generate a report in the repository test-report format |
| `/libs-catalog-seed <app>` | Create or update commercial catalog metadata and preview the Contentful push |
| `/libs-archive-app <app> <reason>` | Archive one app or a small batch |
| `/libs-restore-app <app>` | Restore an archived app to active maintenance |

## Where images come from

All images come from the official project or an authoritative third party (for example, Bitnami). Websoft9 does not maintain these images. Websoft9 verifies the upstream image and Compose configuration so that each package can run directly with `docker compose up` using the provided defaults.

## Documentation

- [Vision](docs/vision.md)
- [Architecture](docs/architecture.md)
- [AI-SDLC Guide](docs/ai-sdlc/README.md)
- [App owner contract](docs/code_owner.md)
- [Maintenance metadata](metadata/maintenance.yaml)
- [Archive metadata](metadata/archive.yaml)
- [Shared skills](skills/README.md)
- [CLI](cli/README.md)
- [Websoft9 Administrator Guide](https://support.websoft9.com/docs/apps)

## Contributing

Community contributions are welcome:

1. Report bugs and propose features through [issues](https://github.com/Websoft9/docker-library/issues).
2. Read [CONTRIBUTING.md](CONTRIBUTING.md) and follow the AI-first delivery flow.
3. Submit pull requests to the `dev` branch and include the latest test report.

## Support

[Websoft9 Enterprise Support](https://www.websoft9.com/apps) covers knowledge, technical support (HTTPS, upgrades), and security services for production deployments.

## License

[LGPL-3.0](LICENSE.md). Additional terms: without authorization, it is not allowed to publish free or paid images based on this repository in any cloud platform's marketplace.

## Disclaimer

We cannot guarantee that third-party open-source software is free of vulnerabilities or security risks. Assessing and accepting those risks is the responsibility of the user under the applicable open-source licenses.
