# Vespa

- 自托管 Vespa 没有 Web UI，也没有内置用户名/密码认证。
- `8080`：应用 HTTP API（查询 / 文档）。**必须先在 `19071` 部署应用包后才会监听**。
- `19071`：config server / 部署端点。全新安装即可用，但**未认证**，暴露到公网需自行加访问控制。
- 部署应用包：`vespa deploy --target http://<host>:19071 ./app`
- 查询示例：`curl 'http://<host>:8080/search/?yql=select * from sources * where true'`
- 启用认证：在应用包 `services.xml` 配置 TLS + 客户端证书（mTLS）或自定义 filter chain；Vespa 内部通信可用 `VESPA_TLS_CONFIG_FILE` 走 mTLS。
