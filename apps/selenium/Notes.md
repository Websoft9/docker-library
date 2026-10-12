# selenium

## FAQ

### 访问方式

- WebDriver API（web）：`http://<host>:${W9_HTTP_PORT_SET}`，健康检查 `http://<host>:${W9_HTTP_PORT_SET}/status`
- noVNC 管理界面（admin）：`http://<host>:${W9_ADMIN_PORT_SET}/?autoconnect=1&resize=scale`，密码为 `.env` 中的 `W9_LOGIN_PASSWORD`（即 `W9_POWER_PASSWORD`）

### 修改 noVNC 密码

`SE_VNC_PASSWORD` 在容器启动时读取。修改 `.env` 中的 `W9_POWER_PASSWORD` 后，重建容器使其生效。

### noVNC 显示黑屏？

Selenium 只在创建 WebDriver 会话时才启动 Chrome；没有活动会话时虚拟桌面为空，因此 noVNC 显示黑屏。这是正常行为，不是故障。先创建一个会话即可在 noVNC 中看到浏览器：

```bash
curl -s -X POST "http://<host>:${W9_HTTP_PORT_SET}/session" \
  -H 'Content-Type: application/json' \
  -d '{"capabilities":{"alwaysMatch":{"browserName":"chrome"}}}'
```

会话结束后浏览器会自动关闭，noVNC 重新变为黑屏。
