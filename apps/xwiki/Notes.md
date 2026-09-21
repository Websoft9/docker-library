# XWiki Notes

> 内部维护说明；面向客户的文档以 `README.md` 为准。

## 来源

- 官方镜像：https://hub.docker.com/_/xwiki
- 镜像源码：https://github.com/xwiki/xwiki-docker
- 版本列表：https://github.com/xwiki/xwiki-platform/releases

## 版本与镜像标签

- `W9_VERSION=18.7` 对应官方 `18.7` 标签（即 `18/mysql-tomcat` 变体，`latest`/`stable` 也指向它）。
- `xwiki` 默认标签就是 mysql-tomcat 变体，无需再加 `-mysql-tomcat` 后缀。
- 官方 compose 通过 `XWIKI_VERSION` 指定具体 XWiki 版本；本包依赖 `18.7` 浮动标签，因此不设置 `XWIKI_VERSION`，随 18.7.x 自动更新。
- 18.7 之前的大版本（LTS `17.10`、中间 LTS `18.4`）仍由官方发布，但本包跟随最新稳定线。

## 数据库

- 内置 MySQL `${W9_ID}-mysql`，镜像 `mysql:${W9_DB_VERSION}`（当前 8.4 LTS）。
- 连接参数：`DB_USER=xwiki`、`DB_DATABASE=xwiki`、`DB_PASSWORD=${W9_POWER_PASSWORD}`、`DB_HOST=${W9_ID}-mysql`。
- `src/mysql_init.sql`（官方 `init.sql`）执行 `grant all privileges on *.* to xwiki@'%'`。这一步是**必需**的：XWiki 迁移要读取 `information_schema` 元数据，需要全局 `PROCESS` 权限，仅 `GRANT ALL ON xwiki.*` 会报 `Access denied; you need (at least one of) the PROCESS privilege(s)`，导致数据库迁移失败（`Database is currently in version [0]`）。
- 启动参数保持官方推荐：`utf8mb4` / `utf8mb4_bin` / `explicit-defaults-for-timestamp=1`（MySQL 8.4 仍接受）。

## 首次安装与升级

- 首次访问会进入 **Distribution Wizard**，会在线下载 Standard Flavor，需要外网，耗时数分钟。
- 管理员账号在向导中创建，不受 `.env` 控制。
- 17.x → 18.x 为大版本升级：先备份 MySQL 数据卷与 `xwiki` 数据卷，升级后按向导完成数据库 schema 迁移。
- 默认使用内嵌 Solr；官方推荐外部 Solr，但需额外挂载配置并处理权限，本包暂不启用。
