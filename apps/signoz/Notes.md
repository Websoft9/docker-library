## SigNoz

#### 如何接入应用监控？

使用 OpenTelemetry SDK 集成到你的应用中,配置 OTLP 导出器指向：
- gRPC: `http://your-ip:4317`
- HTTP: `http://your-ip:4318`

#### 如何自定义仪表板？

将自定义仪表板 JSON 文件放置在 `src/dashboards/` 目录下。

#### 数据保留策略如何配置？

在 `src/clickhouse/config.xml` 中配置 ClickHouse 的 TTL 策略。

#### 如何扩展 ClickHouse 存储？

可以通过修改 `src/clickhouse/cluster.xml` 配置 ClickHouse 集群模式。
