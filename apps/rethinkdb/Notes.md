## RethinkDB

- 可视化界面地址：`http://<host>:8080/`，对外发布为 `W9_HTTP_PORT_SET`。
- 可视化界面没有登录功能，始终以 admin 权限连接；必须通过 Nginx Proxy Manager 的 Access Lists 或防火墙限制访问。
- `admin` 是数据库管理员用户名，密码来自 `.env` 的 `W9_LOGIN_PASSWORD`，仅在数据目录初始化时写入。
- 驱动端口为 `28015`，对外发布为 `W9_DB_PORT_SET`。

### 配置

- `tests/check.sh` 校验驱动端口是否已就绪。
