# Trivy

Trivy runs as a **server**: it keeps the vulnerability database up to date and lets remote clients scan without downloading the DB.

#### Server endpoints

- `http://<host>:<port>/healthz` — health check, returns `ok`
- `http://<host>:<port>/version` — server version information

#### Scan from a client

Install the [Trivy CLI](https://trivy.dev/latest/docs/getting-started/installation/) on the machine that runs the scan, then point it at this server:

```
trivy image --server http://<host>:<port> --token <token> alpine:3.20
trivy fs    --server http://<host>:<port> --token <token> /path/to/project
trivy repo  --server http://<host>:<port> --token <token> https://github.com/org/repo
```

The token is the `W9_LOGIN_PASSWORD` value in `.env` (also shown in the app's **Access** tab).

#### Vulnerability database

The DB is cached in the `trivy_cache` volume (`/root/.cache/trivy`) and refreshed automatically while the server runs.
