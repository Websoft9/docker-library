# Fluent-Bit

## 日志收集

### 示例：收集wordpress的日志
1. 在wordpress容器编排文件中修改日志引擎为fluentd
    ```
    logging:
      driver: fluentd
      options:
        fluentd-address: 47.83.26.60:9001   # url+暴露的端口 （由于Portainer Stack模式只能通过overlay网络相互解析服务名，默认的websoft9是桥接网络，所以不能用服务名加端口查找）
        tag: "wordpress.app"                # 标签，用于区分不同的日志
    ```
2. 编辑fluent-bit.conf
    ```
    [SERVICE]
        Flush        1
        Log_Level    info

    [INPUT]
        Name   forward
        Port   24224
        Listen   0.0.0.0

    [OUTPUT]
        Name   file
        Match  wordpress.app             # 匹配标签
        Path   /var/log/fluentbit        # 日志输出路径（已在编排文件中将该目录映射到外部）
        File  wordpress.log              # 日志文件名（如果不加这一项，则默认按照标签名创建文件）
        Mkdir  On                        # 如果目录不存在，则创建
        Format plain

    [OUTPUT]
        Name   stdout
        Match  *
    ```

官方文档：https://docs.fluentbit.io/manual/