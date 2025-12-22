# KrakenD

KrakenD 是一个高效、开源的 API 网关，旨在简化微服务架构中 API 的管理。
它充当 API 请求的代理，将多个后端服务的响应聚合到一个统一的 API 中，
通常用于提高客户端应用的性能、简化请求结构、并降低复杂性。

# 使用教程

1. 安装后访问应用URL返回健康检测数据即安装成功
2. 如果需要增加端点，可在endpoints中添加一项，以下是最简单的一项配置：
    ```
    {
      "endpoint": "/todos/{id}",                            # kraend 端点
      "method": "GET",                                      # 请求方法
      "output_encoding": "json",                            # 响应编码
      "backend": [
        {
          "url_pattern": "/todos/{id}",                     # 上游url
          "encoding": "json",                               # 上游响应编码
          "sd": "static",
          "method": "GET",                                  # 上游请求方法
          "disable_host_sanitize": false,
          "host": [
            "https://jsonplaceholder.typicode.com"          # 上游服务器
          ]
        }
      ]
    }
    ```
4. 更多配置以及配置说明详见[官方工具](https://designer.krakend.io)以及[官方文档](https://www.krakend.io/docs/configuration/)