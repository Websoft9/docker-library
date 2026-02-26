# Concrete CMS

开源PHP内容管理系统，通过Composer安装并使用CLI进行初始化配置。

## 要点

* 首次启动需要60-90秒完成Composer安装和数据库初始化
* 安装脚本会自动执行 `c5:install` 命令配置CMS
* 管理后台访问路径: `/index.php/dashboard`
* 用户上传的文件存储在 `application/files` 目录

## 路径说明

* 程序根目录: `/var/www/html`
* 配置文件: `/var/www/html/application/config/`
* 上传文件: `/var/www/html/application/files/`
* 缓存目录: `/var/www/html/application/files/cache/`

## FAQ

#### 如何检查安装是否完成？

查看容器日志，确认出现 "Installation Complete!" 消息:
```bash
docker compose logs concrete | grep "Installation Complete"
```

#### 如何重新安装？

清空所有数据卷并重新启动:
```bash
docker compose down -v
docker compose up -d
```

⚠️ 警告：此操作会删除所有内容和数据库！

#### 如何更改管理员密码？

登录后在管理后台 (Dashboard) → Users & Permissions → Members 中修改。
首次登录凭据来自 `.env` 文件的 `W9_LOGIN_USER` 和 `W9_LOGIN_PASSWORD`。

#### 如何增加上传文件大小限制？

编辑 `src/php_extra.ini`:
```ini
upload_max_filesize = 256M
post_max_size = 256M
```
然后重启容器:
```bash
docker compose restart concrete
```
