# Airbyte on Docker

This is an **[Docker Compose template](https://github.com/Websoft9/docker-library)** powered by [Websoft9](https://www.websoft9.com) for [Airbyte](https://airbyte.com).

It uses a two-container pattern:

- `airbyte`: a privileged single-node k3s runtime running inside Docker
- `airbyte-installer`: a one-shot Helm installer that deploys Airbyte into the inner cluster and waits for the real health endpoint

Version model:

- `W9_VERSION` is the Helm chart version passed to `helm upgrade --install --version ...`
- `AIRBYTE_K3S_IMAGE` is the outer runtime image version and is independent from `W9_VERSION`

## System Requirements

The following are the minimal recommended requirements for this package:

- **RAM**: 8 GB or more
- **CPU**: 4 cores or higher
- **Disk**: at least 20 GB of free space
- **Docker**: Docker Engine with Compose v2 and support for privileged containers

## Install

You can install this Airbyte package by following [How to use it?](https://github.com/Websoft9/docker-library#how-to-use-it).

After `docker compose up -d`, the k3s runtime starts first, then Airbyte is installed into the inner cluster. Initial bootstrap may take several minutes, and the app should be considered ready only after the Helm deployment completes and `/api/v1/health` returns success.

## Architecture Notes

- The package does **not** rely on a host Docker socket.
- Kubernetes runs inside the `airbyte` container via k3s.
- Airbyte is installed by Helm chart V2 from `https://airbytehq.github.io/charts`.
- The installer configures the Airbyte server service as a NodePort inside the inner k3s runtime and maps host port `${W9_HTTP_PORT_SET}` to that NodePort.
- Authentication stays enabled. The initial password is predefined through environment variables before Helm install.
- The outer runtime container enforces a single Docker memory cap through `AIRBYTE_RUNTIME_MEMORY_LIMIT`.

## Documentation

- [Deploying Airbyte](https://docs.airbyte.com/platform/deploying-airbyte)
- [Upgrade to Helm chart V2 (Core)](https://docs.airbyte.com/platform/deploying-airbyte/chart-v2-community)
