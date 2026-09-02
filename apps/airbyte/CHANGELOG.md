# CHANGELOG

## 2026-09-02

- Replace the incorrect WordPress-based airbyte package with a real Airbyte package.
- Simplify deployment to a two-container model: privileged k3s runtime plus a one-shot Helm installer.
- Install Airbyte by Helm chart V2 inside the inner k3s cluster.
- Keep authentication enabled and predefine the initial password from environment values before Helm install.
- Make validation wait for the real Airbyte `/api/v1/health` endpoint instead of an outer placeholder page.
- Make `W9_VERSION` the direct Helm chart version input and add a runtime memory cap on the outer k3s container.
