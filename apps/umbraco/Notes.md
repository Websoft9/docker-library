# Umbraco

官方文档：https://docs.umbraco.com/umbraco-cms/get-started/installation/running-umbraco-on-docker-locally

本包基于官方 `Umbraco.Templates` 在构建时生成项目并发布，数据库使用 SQLite，无需额外的数据库容器。

- 后台入口：`/umbraco`
- 管理员账号：首次启动时由 unattended install 使用 `W9_LOGIN_USER` / `W9_LOGIN_PASSWORD` 自动创建
- 数据持久化：`/app/umbraco`（含 SQLite 数据库与日志）、`/app/wwwroot/media`
