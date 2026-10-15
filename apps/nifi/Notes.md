# Apache NiFi

- This package follows the official Docker image's default HTTPS and single-user authentication flow.
- HTTP is intentionally not enabled in this package; validate and redesign the proxy path before changing NiFi to plain HTTP.
- The browser will report a self-signed certificate on first access unless the deployment is customized with trusted certificates.
- `NIFI_WEB_PROXY_HOST` must use the real external hostname; add `hostname:port` when direct HTTPS port access is expected.
