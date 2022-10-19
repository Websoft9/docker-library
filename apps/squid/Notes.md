## Squid

Squid 是一个 web 加速缓存软件，广泛用于 http proxy  

本方案基于 [Datadog 官方镜像](https://hub.docker.com/r/datadog/squid).

主要方案参考：

* [squid详解（正向代理、透明代理、反向代理）](https://www.cnblogs.com/yanjieli/p/7507456.html)
* [How To Setup and Configure a Proxy Server – Squid Proxy](https://devopscube.com/setup-and-configure-proxy-server)

## 参数

* 配置文件： */var/lib/docker/volumes/docker-squid_squid/_data/squid.conf*

## 使用

运行容器之后，有两种快捷的使用方式：

### 无密码访问

1. 配置文件中 http_access deny all 这一行改为：
   ```
   http_access allow all
   ```
2. 重启容器

2. 测试代理
   ```
   curl -x http://47.96.177.178:9091 -L http://www.websoft9.com
   ```

### 有密码访问

1. squid 容器中安装 htpasswd，并创建密码文件
   ```
   apt update
   apt-get install apache2-utils
   touch /etc/squid/passwd
   htpasswd /etc/squid/passwd admin
   ```

2. 修改配置文件，重启容器后生效
   ```
    auth_param basic program /usr/lib64/squid/basic_ncsa_auth /etc/squid/passwd
    auth_param basic children 5
    auth_param basic realm Squid Basic Authentication
    auth_param basic credentialsttl 200 hours
    acl auth_users proxy_auth REQUIRED
    http_access allow auth_users
   ```

4. 测试代理
   ```
   curl -x http://47.96.177.178:9091 --proxy-user admin:12345  -L http://www.websoft9.com
   ```