## Magento

官方提供的 Cloud Docker 项目镜像中，并没有包含 Magento 源码，需在启动容器的时候基于 composer 运行。

有一定的复杂性，故选用 Bitnami 镜像。

## FAQ

#### MAGENTO_HOST 怎么设置？

Magento host domain or IP address. Default: localhost

例如： MAGENTO_HOST=47.243.184.40

也可以运行命令修改 URL
```
magento config:set web/unsecure/base_url  http://47.243.184.40/
```

Nginx Proxy 之后，必须将默认的 8080 改到 80

```
APACHE_HTTP_PORT_NUMBER=80
```

#### CLI in docker image?

yes, `magento -h`

#### How long for Magento init?

5-10 mins 
