# ownCloud

当前软件包已切换为 ownCloud Infinite Scale (`owncloud/ocis`)，不再使用旧版 `owncloud/server` + MySQL + Redis 拓扑。

## FAQ

#### 默认使用 HTTP 还是 HTTPS？

- 当前包按 oCIS 官方默认行为启用 HTTPS。
- 因为启用了 `OCIS_INSECURE=true`，首次部署会使用自签名证书。
- 浏览器首次访问时如果提示证书风险，继续访问即可。

#### 管理员账号如何初始化？

- 用户名固定为 `admin`
- 密码来自 `W9_LOGIN_PASSWORD`
- `IDM_ADMIN_PASSWORD` 只会在首次启动、数据卷为空时生效

#### 域名变化后如何处理？

- `OCIS_URL=https://${W9_URL}:${W9_HTTPS_PORT_SET}` 由包内环境变量生成。
- 修改 `W9_URL` 后需要重建应用，使新 URL 重新注入运行配置。
