# InfluxDB

InfluxDB 是一个时序数据库，Telegraf 是一个数据库收集工具

## 安装

容器启动之后，自行创建账号

## 配置

InfluxDB 支持三种配置方式：

* 配置文件：/etc/influxdb2/config.yml
* 环境变量
* 客户端CLI命令
    ```
    docker run -p 8086:8086 influxdb:2.0 --storage-wal-fsync-delay=15m
    ```

以上配置方式 CLI 配置优先级最高。
