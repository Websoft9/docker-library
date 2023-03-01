# Appname


https://nginxproxymanager.com

## FAQ

#### 如何额外给 Location 增加指令？

直接把指令复制到设置框（通过 location 【齿轮】图标打开）

![image](https://user-images.githubusercontent.com/16741975/198959861-cf09f148-2b7a-42bc-8a43-35882668e974.png)

#### 如何给主 proxy 增加指令？

1. 额外增加一个 / location
2. 填写所需的指令

#### IP 地址是否可以增加 HTTPS？

不可以，Nginxproxymanager 申请证书的时候会报错

#### Advanced 设置作用域？

server 级作用域，非 / location

#### Nginx proxy Manger 如何支持静态网站？

可以支持，具体参考：[Host a Static Site on NGINX Proxy Manager (NPM)](https://dimensionquest.net/2021/02/host-static-site-on-npm/)
