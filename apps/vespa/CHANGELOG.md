# Changelog

## 2026-09-20

- Pin the Vespa image from floating `latest` to `8.751.13`, the newest release with a published image.
- Point `upstream.image` at the Docker Hub registry and add upstream releases and docs references so version scanning works again.
- Rework the compose topology to the official single-container shape running `configserver,services`.
- Map `W9_HTTP_PORT_SET` to the query/document HTTP API (`8080`) and expose the config server / deployment API (`19071`) on `W9_API_PORT_SET`, the endpoint needed for `vespa deploy`.
- Fix data persistence paths to the official `/opt/vespa/var` and `/opt/vespa/logs`; the previous `/var/lib/vespa` and `/etc/vespa` paths do not exist in the image.
- Add a healthcheck against the config server `/state/v1/health`, which is up before any application package is deployed.
- Skip the default web check in `tests/cases.yml`, since the HTTP API on `8080` is not available until an application is deployed.
- Document in the README that Vespa has no web UI or built-in authentication, and how the ports are used.
- Normalize `.env` and `docker-compose.yml` to current repository policy and regenerate `README.md`.
