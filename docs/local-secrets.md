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
| `.secrets/aliyun.env` | Aliyun DNS credentials for `libs dns-bind` / `libs dns-delete` (`ALIYUN_ACCESS_KEY_ID=...`, `ALIYUN_ACCESS_KEY_SECRET=...`, optional `ALIYUN_DNS_DOMAIN=...` wildcard base such as `libs.websoft9.cn`) |

## Manual vs CI

- **Manual / local runs** read from `.secrets/` by default.
- **CI never reads this directory.** CI obtains the same values from GitHub Actions secrets and injects them via environment variables (e.g. `CONTENTFUL_ACCESS_TOKEN`).
- CI should derive tags and build arguments from `libs app-build-plan`; `libs app-build --push` remains available as an owner/maintainer fallback when CI cannot be used.

## Rules

- Never commit secrets; keep files under `.secrets/` outside git.
- Keep `.secrets/ssh/default.pem` with permissions `600`.
- Run `make remote` to regenerate `.secrets/remote.env` interactively; the default deploy root is `/websoft9/library/apps`.
- Run `make connector` to create or update provider token files such as `.secrets/contentful.env`, `.secrets/cloudflare.env`, `.secrets/dockerhub.env`, and `.secrets/aliyun.env` interactively.
- Provider env files store the token directly as standard environment variables; no extra file indirection is used.
- `libs dns-bind` points the wildcard record (`*.<ALIYUN_DNS_DOMAIN>`) at the remote host or `127.0.0.1`; `libs dns-delete` removes that single record. They read `TARGET`/`SSH_HOST` from `.secrets/remote.env` unless `--target`, `--ip`, or `--ssh-host` is given.
- After a successful bind, `libs dns-bind` also sets the platform domain by running `websoft9 setconfig --section domain --key wildcard_domain` inside the Websoft9 container. The container name is the shared CLI default (`CONTAINER` in `.secrets/remote.env`, else `websoft9`), not hardcoded. This step is best-effort: it is skipped without error when the container is missing or unreachable, and `--no-container` disables it.
- `DOCKERHUB_ORG` is the default namespace for publishing: a bare `W9_REPO` (e.g. `wordpress`) becomes `<org>/wordpress`, while an already-namespaced `W9_REPO` (e.g. `websoft9dev/akeneo`) is kept as-is. Override per run with `--org`; it never affects deploy builds (only push targets).
- `libs app-build --push` is a controlled backdoor: outside CI, pushing stable tags requires `--confirm-stable`.
