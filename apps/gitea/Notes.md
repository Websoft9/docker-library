# Gitea

## FAQ

#### gitea:-rootless 镜像有什么特征？

The rootless image use Gitea internal SSH to provide Git protocol and doesn’t support OpenSSH.

#### 配置文件怎么处理？

1. 容器启动后，有一个配置文件：gitea/conf/app.ini
2. 官方表名支持[自定义配置文件](https://docs.gitea.io/zh-cn/install-with-docker/#%E8%87%AA%E5%AE%9A%E4%B9%89)，但是自定义的配置文件是整个覆盖原生的，还是仅覆盖配置项有待研究
