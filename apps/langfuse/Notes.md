# Langfuse

开源的 LLM (大语言模型) 工程平台,提供可观测性、提示管理、评估和追踪功能。

## 要点

* **首次访问**: 访问 Web 界面后,首次用户需通过 UI 注册账户,该账户自动成为组织 Owner
* **多服务架构**: 需要 6 个容器协同工作 (Web + Worker + PostgreSQL + ClickHouse + Redis + MinIO)
* **启动时间**: 首次启动约需 60-90 秒,等待所有依赖服务健康检查通过
* **容器路径**: 
  - PostgreSQL 数据: `/var/lib/postgresql/data`
  - ClickHouse 数据: `/var/lib/clickhouse`
  - MinIO S3 数据: `/data`

## FAQ

#### 为什么没有预设的管理员账户？

Langfuse 使用 NextAuth.js 认证框架,不提供固定管理员账户。首次访问时你需要通过 UI 注册第一个用户,该用户自动成为 Owner 角色。如果需要预创建账户,可以使用 `LANGFUSE_INIT_USER_*` 环境变量(非必需)。

#### 容器启动失败或健康检查超时？

由于涉及 6 个服务的顺序启动,首次部署可能需要较长时间:
- PostgreSQL 初始化: ~10-15 秒
- ClickHouse 初始化: ~20-30 秒
- Redis/MinIO 初始化: ~5 秒

建议等待至少 2 分钟后再检查容器状态。如果问题持续,检查 `docker compose logs` 查看具体错误。

#### 如何访问 MinIO 管理控制台？

MinIO 控制台绑定在本地端口 9091 (http://127.0.0.1:9091),只能从宿主机访问。S3 API 端口 9090 可以通过 `W9_MINIO_PORT_SET` 设置外部访问端口。默认凭据:
- 用户名: minio
- 密码: $W9_POWER_PASSWORD (查看 .env 文件)

#### 如何配置外部 S3 存储而非 MinIO？

修改 .env 文件中的 S3 相关变量:
```env
LANGFUSE_S3_EVENT_UPLOAD_ENDPOINT=https://s3.amazonaws.com
LANGFUSE_S3_EVENT_UPLOAD_ACCESS_KEY_ID=<your_key>
LANGFUSE_S3_EVENT_UPLOAD_SECRET_ACCESS_KEY=<your_secret>
LANGFUSE_S3_EVENT_UPLOAD_REGION=us-east-1
```
然后可以移除 docker-compose.yml 中的 minio 服务定义。

#### 数据如何持久化？

所有数据通过 Docker 命名卷持久化:
- `langfuse_postgres_data`: 用户数据、项目配置
- `langfuse_clickhouse_data`: 追踪数据、分析数据
- `langfuse_minio_data`: 媒体文件、事件文件

重启容器或升级版本不会丢失数据。如需备份,备份这些卷即可。
