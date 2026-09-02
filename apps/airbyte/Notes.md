# Airbyte

## FAQ

- This package boots a privileged `k3s` runtime in the main `airbyte` container, then a one-shot installer deploys Airbyte into that inner Kubernetes cluster by Helm.
- There is no outer proxy or placeholder page. The public port maps directly to the Airbyte NodePort inside k3s.
- `W9_VERSION` drives the Helm chart version used by the installer; it does not change the outer k3s runtime image.
- Readiness should be judged by the real Airbyte `/api/v1/health` endpoint, not by the compose containers alone.
- The package is aimed at demo, development, or lightweight lab usage rather than production.
