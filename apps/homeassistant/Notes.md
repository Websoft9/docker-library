# Home Assistant

Need add **mosquitto MQTT** for this application.

`src/nginx-proxy.conf` is shipped: the gateway clears `X-Forwarded-For` /
`X-Real-IP` so Home Assistant does not reject domain requests, and forwards the
WebSocket upgrade.

## FAQ

### Port works but a bound domain returns HTTP 400

Home Assistant blocks requests that carry forwarded headers unless the proxy is
a trusted proxy. Because `http:` in `configuration.yaml` is ignored since HA
2026.8, the settings live under **Settings > System > Network** (Trust
X-Forwarded-For + Trusted proxies). The shipped `src/nginx-proxy.conf` avoids the
problem by dropping those headers at the gateway. If you prefer real client IPs
and IP banning, remove the two `proxy_set_header` lines that clear
`X-Forwarded-For` / `X-Real-IP` and instead enable the trusted-proxy settings in
the UI.
