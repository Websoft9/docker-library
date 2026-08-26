# Local Secrets and Remote Defaults

This repository keeps local secrets and remote execution defaults outside git.

## `.secrets/` directory

`.secrets/` holds **local defaults for manual or human invocation only**. It is git-ignored (see `.gitignore`), so nothing under it is ever committed.

| Path | Purpose |
| --- | --- |
| `.secrets/remote.env` | Remote execution profile written by `make remote` (TARGET, SSH_HOST, SSH_USER, SSH_SECRET_PATH, DEPLOY_ROOT). Template: `metadata/templates/remote.env.example` |
| `.secrets/ssh/default.pem` | Default SSH key for remote deploy-validation (chmod 600) |
| `.secrets/contentful.key` | Contentful management token for `libs contentful-create --apply` |
| `.secrets/cloudflare_r2` | Cloudflare R2 credentials for publish operations |

## Manual vs CI

- **Manual / local runs** read from `.secrets/` by default.
- **CI never reads this directory.** CI obtains the same values from GitHub Actions secrets and injects them via environment variables (e.g. `CONTENTFUL_ACCESS_TOKEN`).

## Rules

- Never commit secrets; keep files under `.secrets/` outside git.
- Keep `.secrets/ssh/default.pem` with permissions `600`.
- Run `make remote` to regenerate `.secrets/remote.env` interactively; the default deploy root is `/websoft9/library/apps`.
