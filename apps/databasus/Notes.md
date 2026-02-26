# Databasus

Self-hosted database backup management tool with embedded PostgreSQL and Valkey.

## 要点

* 首次访问时需要通过 Web UI 注册管理员账户，无预配置凭据
* 内嵌 PostgreSQL 17 和 Valkey 缓存，无需外部数据库
* 数据存储在 `/databasus-data` 卷中（包含数据库数据、备份文件和加密密钥）
* 支持 PostgreSQL 12-18、MySQL、MariaDB、MongoDB 的自动备份

## FAQ

#### 首次启动较慢？

内嵌 PostgreSQL 需要初始化，首次启动可能需要 1-2 分钟。

#### 如何重置管理员密码？

```bash
docker exec -it databasus ./main --new-password="new_password" --email="admin@example.com"
```
