## Summary

<!-- Briefly describe what this PR does and why. -->

## Changed Apps

<!-- pr-bot:apps-table -->
_🤖 Bot will fill this in automatically when the PR is opened or updated._
<!-- pr-bot:apps-table-end -->

## Type of Change

<!-- pr-bot:change-type -->
- [ ] 🆕 New app
- [ ] 🔄 Version update
- [ ] 🛠 Config / compose fix
- [ ] 🐛 Bug fix
- [ ] 📄 Documentation
- [ ] 🔧 CI / build tooling
<!-- pr-bot:change-type-end -->

## Checklist

- [ ] `.env` — `W9_VERSION` 设置了具体版本号（不为 `latest`）
- [ ] `.env` — `W9_LOGIN_USER` / `W9_LOGIN_PASSWORD` 仅在 app 有内置认证时填写
- [ ] `.env` — `W9_URL_REPLACE=true` 仅在 `docker-compose.yml` 中引用了 `$W9_URL` 时填写
- [ ] `docker-compose.yml` — 所有 `./src/*` 映射的文件在 `src/` 目录中存在
- [ ] `docker-compose.yml` — 所有 service 设置了 `restart: unless-stopped`
- [ ] `apps/{name}/CHANGELOG.md` — 版本更新或 compose 变更时已更新
- [ ] 本地已用 `docker compose up -d` 测试启动成功
- [ ] 已用 `docker compose down -v` 清理测试环境

## Notes

<!-- Any additional context, screenshots, or caveats. -->
