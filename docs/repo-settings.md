# GitHub 仓库配置说明

本文件记录 docker-library 仓库所需的 GitHub Settings 配置，便于仓库迁移或重建时复现。

---

## Branch Protection Rules

> ⚠️ **这是所有 CI 门控生效的前提。** 如不配置，拥有写权限的人可以直接 push 绕过所有 Gates。

进入路径：GitHub → Settings → Branches → Add branch protection rule

### `dev` 分支规则

| 配置项 | 值 |
|--------|-----|
| Branch name pattern | `dev` |
| Require a pull request before merging | ✅ 启用 |
| Required number of approvals | 1 |
| Dismiss stale reviews when new commits are pushed | ✅ 启用 |
| Require status checks to pass before merging | ✅ 启用 |
| Require branches to be up to date before merging | ✅ 启用 |
| Do not allow bypassing the above settings | ✅ 启用（含管理员） |
| Restrict who can push to matching branches | 仅 maintainers |

**必须通过的 Status Checks（搜索并添加）：**

```
validate        （来自 validate.yml）
image-check     （来自 image-check.yml，Phase 2 完成后添加）
smoke-test      （来自 pull_quest_test.yml）
```

### `main` 分支规则

| 配置项 | 值 |
|--------|-----|
| Branch name pattern | `main` |
| Require a pull request before merging | ✅ 启用 |
| Required number of approvals | 1（或 2） |
| Dismiss stale reviews when new commits are pushed | ✅ 启用 |
| Require status checks to pass before merging | ✅ 启用 |
| Do not allow bypassing the above settings | ✅ 启用（含管理员） |
| Restrict who can push to matching branches | 仅 maintainers |

**必须通过的 Status Checks：**

```
pr-to-main-gate （来自 pr-to-main.yml，Phase 2 完成后添加）
```

---

## GitHub CLI 配置方式（可选）

如需通过代码管理，可使用 GitHub CLI：

```bash
# dev 分支保护
gh api repos/{owner}/{repo}/branches/dev/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["validate","smoke-test"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field restrictions=null

# main 分支保护
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["pr-to-main-gate"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field restrictions=null
```

---

## Secrets 配置

进入路径：GitHub → Settings → Secrets and variables → Actions

| Secret 名称 | 用途 |
|------------|------|
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare R2 账户 ID |
| `CLOUDFLARE_R2_SECRET_ID` | R2 Access Key ID |
| `CLOUDFLARE_R2_SECRET_KEY` | R2 Secret Access Key |
| `CLOUDFLARE_ZONE_ID` | CDN 缓存清除 Zone ID |
| `CLOUDFLARE_API_TOKEN` | CDN 缓存清除 Token |
| `MYGITHUB_ADMIN_TOKEN` | 触发下游仓库 workflow 的 PAT |
| `ZJ_ADMIN_TOKEN` | i18n PR 到插件仓库的 PAT |
| `DOCKER_USERNAME` | Docker Hub 推送用户名 |
| `DOCKER_PASSWORD` | Docker Hub 推送密码 |
| `DINGTALK_WEBHOOK` | 钉钉告警 Webhook（可选） |

> 建议每 90 天轮换一次 PAT 类 Secret（`MYGITHUB_ADMIN_TOKEN`、`ZJ_ADMIN_TOKEN`）。
