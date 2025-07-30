# KrakenD

KrakenD 是一个高效、开源的 API 网关，旨在简化微服务架构中 API 的管理。
它充当 API 请求的代理，将多个后端服务的响应聚合到一个统一的 API 中，
通常用于提高客户端应用的性能、简化请求结构、并降低复杂性。

# 使用教程

1. 安装后访问应用URL返回健康检测数据即安装成功
2. 通过官方工具[KrakenDesigner](https://designer.krakend.io) 生成配置文件
    - 在 Service settings 标签页的 Hosts 下添加上游API服务器
    - 在 Endpoints 标签页添加API路由，配置请求的源URL、目标服务器、目标URL等信息
    - 配置完成后点击右上角Download config下载配置文件
    > **注意**：该应用为社区开源版，带有`Enterprise`标签的功能无法使用
3. 将生成的配置文件替换仓库中的`src/krakend.json`文件，然后重建应用生效