# Codeserver

https://hub.docker.com/r/linuxserver/code-server 

这个项目考虑非常全面。

## FAQ

#### 如何安装 Node 环境？

```
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install --global yarn
```
> yarn 一定要通过 npm 安装，apt 安装的 yarn 无法直接使用


#### Terminal 构建后的预览页面如何浏览？

有两个方案：

- docker-compose.yml 文件中绑定一个容器端口到宿主机，构建时指定此端口。例如：npm run start -- --host 0.0.0.0  --port 3002
- 使用 Websoft9 控制台的【网关】为预览端口做一个代理，这样不需要绑定端口到宿主机

#### 终端如何切换到 root 用户？
```
$ sudo su

手动输入密码或ctrl+V 拷贝密码
```