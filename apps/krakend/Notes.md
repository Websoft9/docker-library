# KrakenD

KrakenD 是一个高效、开源的 API 网关，旨在简化微服务架构中 API 的管理。
它充当 API 请求的代理，将多个后端服务的响应聚合到一个统一的 API 中，
通常用于提高客户端应用的性能、简化请求结构、并降低复杂性。

# 使用教程

1. 通过官方工具 https://designer.krakend.io/#!/ 生成配置文件
2. 将生成的配置文件移动至数据卷 `krakend` 中
3. 重启 KrakenD 服务生效