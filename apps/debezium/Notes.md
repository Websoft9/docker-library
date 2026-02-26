# Debezium

Debezium Server 没有 Web UI，所有配置通过 `src/application.properties` 文件完成。

## 要点

* 使用前必须编辑 `src/application.properties`，配置源数据库连接和 Sink 目标，否则容器启动后会因缺少有效配置而报错
* 支持的源数据库：PostgreSQL、MySQL、MongoDB、SQL Server、Oracle 等，通过 `debezium.source.connector.class` 切换
* 支持的 Sink 类型：http、kafka、kinesis、pubsub、redis、rabbitmq、mqtt、nats
* Offset 数据持久化在 Docker 命名卷 `debezium_data` 中，删除此卷会导致 CDC 位点重置

## FAQ

#### 如何切换源数据库类型？

修改 `src/application.properties` 中 `debezium.source.connector.class` 为对应的连接器类名，同时更新数据库连接参数，然后重启容器。

#### 如何检查服务是否正常运行？

`curl http://localhost:9001/q/health` 返回 `{"status":"UP"}` 表示正常。

#### Offset 数据存储在哪里？

默认使用文件存储，路径为容器内 `/debezium/data/offsets.dat`（映射到 `debezium_data` 命名卷）。也可配置为 Redis 或 JDBC 存储。
