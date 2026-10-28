# GitHub Settings Spec

Repository settings required by the current CI/CD workflows.

## Settings

| Location | Required configuration |
| --- | --- |
| Copilot → cloud agent | Enable the agent; disable **Require approval for workflow runs**. |
| Rules → `main-protection` | Require PRs and the **PR checks** check; required approvals **0**; squash merge and linear history; prohibit force pushes/deletion. Merge remains manual. |
| Actions → General | Enable the actions referenced in `.github/workflows/`. Jobs declare their own `permissions`; changing the default to write is not a substitute. |
| Pages → Build and deployment | Source: **GitHub Actions**. The `github-pages` environment must allow release tags. |
| Environments | No required reviewers for automatic E2E/publishing jobs. |

**Allow GitHub Actions to create and approve pull requests** is a separate Actions setting. Enable it when using `GITHUB_TOKEN` for those operations; it does not grant administrator permissions or guarantee that every PR mutation is allowed. The current Ready step uses a user PAT instead.

## GitHub credentials

Configure custom secrets under **Secrets and variables → Actions → Secrets**.

| Name | Purpose |
| --- | --- |
| `GITHUB_TOKEN` / `github.token` | Automatically issued per job; do not create it manually. Repository-scoped GitHub App token, restricted by job permissions and organization policies. Used for checks, releases, and ordinary repository API calls. |
| `MAINTENANCE_STATE_TOKEN` | User PAT for maintenance state, Copilot assignment, and PR Ready. One PAT can cover these operations; the user must have repository access and Copilot eligibility. Current workflows support a classic PAT with `repo` scope; fine-grained tokens need the corresponding Variables, Issues, Pull requests and read permissions. |
| `COPILOT_ASSIGN_TOKEN` | Optional override for assignment and PR Ready. Leave unset to reuse `MAINTENANCE_STATE_TOKEN`; a second PAT is not required. |

`permissions:` only controls `GITHUB_TOKEN`, not PAT permissions. `GH_TOKEN` is the environment variable used by `gh`; its rights depend on which credential the workflow puts there. Settings cannot turn `GITHUB_TOKEN` into a user identity or give it repository-variable write access.

## Other CI/CD secrets

| Feature | Secret names |
| --- | --- |
| E2E server | `ALIYUN_ACCESS_KEY_ID`, `ALIYUN_ACCESS_KEY_SECRET`, `ALIYUN_SSH_PRIVATE_KEY` |
| WeCom notifications | `WECOM_WEBHOOK` |
| Contentful | `CONTENTFUL_TOKEN`, `CONTENTFUL_GRAPHQLTOKEN` |
| R2 publishing | `CLOUDFLARE_R2_SECRET_ID`, `CLOUDFLARE_R2_SECRET_KEY`, `CLOUDFLARE_ACCOUNT_ID` |
| Cloudflare cache purge | `CLOUDFLARE_ZONE_ID`, `CLOUDFLARE_API_TOKEN` |
| DockerHub publishing | `DOCKER_USERNAME`, `DOCKER_PASSWORD` |

The maintenance workflow creates/updates the **Actions variable** `MAINTENANCE_SCAN_STATE`; it is not a secret.

## Verification

One update issue normally produces assignment → agent → PR checks/E2E, followed by manual merge. If a GitHub API operation fails, inspect the exact step error and its job token permissions before changing settings or adding credentials.
