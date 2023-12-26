# NextCloud

## 安装

NextCloud 容器安装注意事项：

1. NextCloud 与 MySQL 版本匹配问题
2. 受信域名问题([issues #3](https://github.com/Websoft9/docker-nextcloud/issues/3))

## 重置密码

Nextcloud does not support password resets from environment variables. If you want to change your password run the following commands in your terminal:

```
sudo docker exec -u www-data -it nextcloud /bin/bash
php occ user:resetpassword username
```


