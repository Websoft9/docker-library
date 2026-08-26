# ActiveMQ Notes

> 内部排障与维护要点。客户文档以 `README.md` 为准（由 `W9_*` 标记区注入手写内容）。

## 来源

- 官方镜像：https://hub.docker.com/r/apache/activemq
- 官方 Docker 说明：https://github.com/apache/activemq/tree/main/assembly/src/docker
- 仅 Classic 版；`W9_VERSION=6.3.0`，兼容 5.19.x / 6.2.x 镜像

## 镜像修补（`src/entrypoint.sh`）

按版本布局自动适配，启动时幂等修补 Web Console：

| 版本 | 布局 | 修补 |
| --- | --- | --- |
| 5.19.x / 6.2.x | 单体 `conf/jetty.xml`（Spring bean） | 白名单追加 `0.0.0.0/0`/`::/0`；5.19 额外同步 jetty-realm 密码、移除 CSP `upgrade-insecure-requests` |
| 6.3.x | modular `conf/jetty/jetty-security.xml` | 白名单 `<Item>` 追加 |

- 403 根因：InetAccessHandler 白名单默认仅 loopback；需 CIDR `0.0.0.0/0`（`0.0.0.0` 字面不生效）
- 5.19 认证：Web Console 读 `jetty-realm.properties`（entrypoint 只写 users.properties，需额外同步）
- 重启循环：镜像 CMD 被 override 为 null 时 `$@` 为空，脚本兜底补 `activemq console`

## 排障

- `docker ps`：activemq 必须 `Up`，`Restarting` 看 `docker logs`
- `curl -w "%{http_code}" http://<host>:8161/admin`：401=白名单已放行待认证；403=白名单未生效
- 升级版本后必验：无重启、8161 无 403、登录成功、CSP 头无 `upgrade-insecure-requests`

## Functional Checks

部署验证时的三项功能检查（AI / 自动测试执行）：

1. **Console 可登录**
   ```bash
   curl -s -o /dev/null -w "%{http_code}" -u admin:<PASSWORD> http://<host>:8161/admin/   # 期望 200
   ```

2. **凭据可更改**
   修改 `.env` 的 `W9_LOGIN_PASSWORD` 后 `docker rm` + 重建容器；期望旧密码 401、新密码 200。
   （注意：仅 restart 不生效，须重建。）

3. **Send 功能成功**
   在 Console 的 Send 页向一个临时队列发送一条消息，再经 Jolokia 读取入队计数增量：
   ```bash
   curl -u admin:<PASSWORD> "http://<host>:8161/api/jolokia/read/org.apache.activemq:brokerName=localhost,type=Broker/TotalEnqueueCount"
   ```

## 变更

- 2026-08：移除 Artemis，官方镜像；README 采用 `W9_GUIDE/NOTE/TROUBLESHOOT/CHANGELOG` 标记区，成为客户文档唯一来源
