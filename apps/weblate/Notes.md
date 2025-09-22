# Weblate

1、Websoft9 控制台安装 Weblate 后，通过**我的应用**查看应用详情，在**访问**标签页中获取访问URL。

2、在**访问**标签页中获取初始账号，完成登录后请修改账户。

3、配置SMTP（可选）：
- 通过**我的应用**查看应用详情，在**编排**标签页中选择修改当前应用git仓库；
- 在.env文件内配置对应SMTP环境变量配置；
- 修改成功后重建应用。

## 配置要点

### 初始设置
- 默认管理员邮箱：由 `WEBLATE_ADMIN_EMAIL` 环境变量设置
- 默认管理员密码：由 `WEBLATE_ADMIN_PASSWORD` 环境变量设置
- 网站域名：由 `WEBLATE_SITE_DOMAIN` 环境变量设置

### 数据库连接
- 使用 PostgreSQL 17-alpine 作为数据库
- 连接字符串：`postgresql://weblate:password@weblate-db/weblate`
- 数据持久化存储在 `postgres_data` 卷中

### 缓存设置
- 使用 Redis 8-alpine 作为缓存服务器
- 缓存主机：`weblate-cache`
- 数据持久化存储在 `redis_data` 卷中

### 国际化支持
- 时区设置：UTC（可通过 `WEBLATE_TIME_ZONE` 修改）
- 支持多语言界面和翻译项目管理

### 注册设置
- 默认开启用户注册（`WEBLATE_REGISTRATION_OPEN=1`）
- 支持邮箱注册验证

### SMTP 邮件配置
在 .env 文件中取消注释并配置相关 SMTP 变量：
```
WEBLATE_EMAIL_HOST=smtp.example.com
WEBLATE_EMAIL_PORT=587
WEBLATE_EMAIL_HOST_USER=your-email@example.com
WEBLATE_EMAIL_HOST_PASSWORD=your-app-password
WEBLATE_EMAIL_USE_TLS=1
WEBLATE_SERVER_EMAIL=weblate@example.com
WEBLATE_DEFAULT_FROM_EMAIL=weblate@example.com
```
