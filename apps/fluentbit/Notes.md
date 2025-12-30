# Fluent-Bit

## 日志收集

### 示例：监控收集cpu指标并存储到指定文件
1. 编辑fluent-bit.conf
    ```
    [SERVICE]
        Flush         1
        Log_Level     info

    [INPUT]
        Name          cpu
        Tag           my_cpu                # 设置标签
        Interval_Sec  1                     # 1秒间隔
        Threaded      true

    [OUTPUT]
        Name          file
        Match         my_cpu                # 匹配标签
        Path          /var/log/fluentbit    # 日志输出路径（已在编排文件中将该目录映射到外部）
        File          cpu.log               # 日志文件名（如果不加这一项，则默认按照标签名创建文件）
        Mkdir         On                    # 如果目录不存在，则创建

    [OUTPUT]
        Name   stdout
        Match  *
    ```

官方文档：https://docs.fluentbit.io/manual/