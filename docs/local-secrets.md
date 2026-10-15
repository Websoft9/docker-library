# Local Secrets and Remote Defaults

This repository keeps local secrets and remote execution defaults outside git.

## `.secrets/` directory

`.secrets/` holds **local defaults for manual or human invocation only**. It is git-ignored (see `.gitignore`), so nothing under it is ever committed.

| Path | Purpose |
| --- | --- |
| `.secrets/remote.env` | Remote execution profile written by `make remote` (TARGET, SSH_HOST, SSH_USER, SSH_SECRET_PATH, DEPLOY_ROOT, CONTAINER). Template: `metadata/templates/remote.env.example` |
| `.secrets/ssh/default.pem` | Default SSH key for remote deploy-validation (chmod 600) |
| `.secrets/contentful.env` | Contentful token file for `libs catalog-push --apply` (`CONTENTFUL_ACCESS_TOKEN=...`) |
| `.secrets/cloudflare.env` | Cloudflare token file for CLI or publish operations (`CLOUDFLARE_API_TOKEN=...`) |
| `.secrets/dockerhub.env` | Docker Hub credentials for the controlled `libs app-build --push` backdoor (`DOCKERHUB_USERNAME=...` and `DOCKERHUB_TOKEN=...`, optional `DOCKERHUB_ORG=...` default push namespace) |
| `.secrets/dns.env` | DNS credentials for `make dns-bind` / `make dns-delete` (`DNS_PROVIDER=...` such as `aliyun`, `DNS_KEY_ID=...`, `DNS_KEY_SECRET=...`, optional `DNS_DOMAIN=...` wildcard base such as `libs.websoft9.cn`) |
| `.secrets/aliyun.env` | Alibaba Cloud credentials written by `make connector` → `alibabacloud` (`ALIYUN_ACCESS_KEY_ID=...`, `ALIYUN_ACCESS_KEY_SECRET=...`, optional `ALIYUN_REGION=...`) |
| `.secrets/aws.env` | AWS credentials written by `make connector` → `aws` (`AWS_ACCESS_KEY_ID=...`, `AWS_SECRET_ACCESS_KEY=...`, optional `AWS_REGION=...`) |
| `.secrets/azure.env` | Azure credentials written by `make connector` → `azure` (`AZURE_SUBSCRIPTION_ID=...`, `AZURE_TENANT_ID=...`, `AZURE_CLIENT_ID=...`, `AZURE_CLIENT_SECRET=...`) |

## Manual vs CI

- **Manual / local runs** read from `.secrets/` by default.
- **CI never reads this directory.** CI obtains the same values from GitHub Actions secrets and injects them via environment variables (e.g. `CONTENTFUL_ACCESS_TOKEN`).
- CI should derive tags and build arguments from `libs app-build-plan`; `libs app-build --push` remains available as an owner/maintainer fallback when CI cannot be used.

## Rules

- Never commit secrets; keep files under `.secrets/` outside git.
- Keep `.secrets/ssh/default.pem` with permissions `600`.
- Run `make remote` to regenerate `.secrets/remote.env` interactively; the default deploy root is `/websoft9/library/apps`.
- Run `make connector` to create or update provider files interactively: `contentful`, `cloudflare`, `dockerhub`, `dns` (`.secrets/dns.env`, asks for a `DNS_PROVIDER` defaulting to `aliyun`, key id, key secret, and the wildcard base domain), and the cloud providers `alibabacloud` (`.secrets/aliyun.env`), `aws` (`.secrets/aws.env`), and `azure` (`.secrets/azure.env`).
- Provider env files store the token directly as standard environment variables; no extra file indirection is used.
- `make dns-bind` points the wildcard record (`*.<DNS_DOMAIN>`) at the remote host or `127.0.0.1`; `make dns-delete` removes that single record. They read `TARGET`/`SSH_HOST` from `.secrets/remote.env` unless `--target`, `--ip`, or `--ssh-host` is given. Only `DNS_PROVIDER=aliyun` is implemented today; other providers are rejected with a clear error.
- After a successful bind, `make dns-bind` also sets the platform domain by running `websoft9 setconfig --section domain --key wildcard_domain` inside the Websoft9 container. The container name is the shared CLI default (`CONTAINER` in `.secrets/remote.env`, else `websoft9`), not hardcoded. This step is best-effort: it is skipped without error when the container is missing or unreachable, and `--no-container` disables it.
- `DOCKERHUB_ORG` is the default namespace for publishing: a bare `W9_REPO` (e.g. `wordpress`) becomes `<org>/wordpress`, while an already-namespaced `W9_REPO` (e.g. `websoft9dev/akeneo`) is kept as-is. Override per run with `--org`; it never affects deploy builds (only push targets).
- `libs app-build --push` is a controlled backdoor: outside CI, pushing stable tags requires `--confirm-stable`.
