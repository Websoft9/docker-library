## Rancher

Rancher 是 K8S 的一种GUI发行版，大大简化 K8S 的使用。它可以基于容器安装。

### Install

Ranker need https, simple installation below:

```
docker run -d --restart=unless-stopped \
  -p 9015:80 -p 9016:443 \
  --privileged \
  rancher/rancher:latest
```

> 它需直接访问 HTTP 端口
