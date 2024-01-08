# Traefik

- 目前的配置文件默认支持 Docker 服务，k8s 下未研究
- 8080 端口由于安全考虑，没有直接绑定到宿主机。Nginx proxy 的 location /dashboard {} 方案也无法达成目标
