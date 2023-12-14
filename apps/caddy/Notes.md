## Caddy

### Caddyfile

Caddyfile如果在docker-compose里面使用本地volumes，一定不能为空，通常需要设置下列项目：
1. 监听端口
2. 设置网站根目录
3. 启用静态文件服务器

 > Caddy 的docker compose文件里面，容器内部端口不能使用变量，否则报错


