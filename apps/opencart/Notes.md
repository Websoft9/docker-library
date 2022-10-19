# OpenCart

已经弃用 Bitnami 镜像，改用自行开发的 Dockerfile

## 常见问题

#### Dashboard 要求转移 storage 文件夹，可以吗？
不可以，会导致 storage 权限发生变化，从而出现代码错误

#### 可以将 /var/www 设置为 volume 吗？
不可以，会导致代码错误

## Bitnami 归档

直接运行 Bitnami 中的 docker-compose 文件，首页乱码。

已经向官方提供issue：https://github.com/bitnami/bitnami-docker-opencart/issues/102

**疑难**

目前还未掌握 OPENCART_HOST 环境变量的使用

OPENCART_HOST 对应服务器IP或者机器名，目前访问混乱的原因是所有静态资源无法访问（js,css,images）。
需要将OPENCART_HOST配置成IP+映射端口的模式，详见 docker-compose 文件.
