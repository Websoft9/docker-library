# Akeneo

本应用需要重新编写，建议采用官方的 make 方案。

> 官方并没有计划提供一个开箱即用的社区版镜像，故我们也没有必要维护。

## 安装

先阅读官方文档：https://docs.akeneo.com/master/install_pim/docker/installation_docker.html

### 镜像寻找

没有找到满足需求的镜像，故需研究安装方案。


### 解读

官方仅提供了定制的 [PHP 镜像](https://hub.docker.com/r/akeneo/pim-php-base)，其中仅包含了 php, php-cli, fpm。这个镜像并没有包含 Akeneo 源码，且是用于测试，非生产环境。

经过大量的试错和研究，最终得出 Akeneo 精准的安装要素如下：

* 环境：php, php-cli, php-fpm, node, yarn, composer
* 外部应用：mysql8.0, es7.10

安装步骤除了通过 composer 实现后端 PHP 源码的完整性之外，一定要在所有环境和应用连接成功后，再运行 `NO_DOCKER=true make prod` 完成前端完整性以及数据导入。


### 方案

目前确认可行的方案是基于 Akeneo 官方镜像的基础上进行研发，具体需求：

* 安装 apache 以及连接 php-fpm
* 安装 Akeneo，提取数据库连接和管理员账号的环境变量
* Apache 日志转发到 docker logs
* Apache 服务的健壮性研究

## 常见问题

#### make prod 成功之后，仍然无法访问？

需修正访问根目录的权限 ： chown -R www-data:www-data /var/www/html

#### 默认的账号密码是什么？

开发者模式下是 admin/admin，生产模式下需自行创建
```
bin/console pim:user:create admin admin support@example.com Admin Admin en_US --admin -n --env=prod
```

#### 初始化需要什么条件？

需配置正确的数据库连接，否则无法完成初始化

#### 容器初始化时间长吗？

约5-8分钟，依赖 node 在线安装。国内服务器需考虑这个网络情况
