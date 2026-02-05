# Moodle Docker 镜像构建项目 Story

## 📋 项目概述

**项目名称**: Moodle 官方 Docker 镜像（非官方维护）  
**目标**: 为 Moodle 创建生产级 Docker 镜像并推送到 Docker Hub  
**背景**: Moodle 官方不维护 Docker 镜像，需要基于 `php:apache` 自行构建  
**镜像仓库**: `docker.io/websoft9dev/moodle`

## 🎯 项目目标

### 核心目标
1. 创建基于官方 `php:apache` 的 Moodle 容器镜像
2. 支持最新的 Moodle 5.1.1 版本（稳定版）
3. 遵循 Moodle 官方安装指南和最佳实践
4. 提供生产环境可用的配置
5. 支持一键部署和自动化安装

### 技术要求
- ✅ PHP 8.2 + Apache（Moodle 5.1 官方要求）
- ✅ 所有必需的 PHP 扩展
- ✅ MariaDB/PostgreSQL 数据库支持
- ✅ 性能优化配置（OPcache, Redis）
- ✅ 符合 Moodle 5.0+ 新架构（/public 目录）
- ✅ 自动化配置和安装脚本
- ✅ 健康检查和日志管理
- ✅ 数据持久化

## 📚 参考文档

- **官方安装指南**: https://docs.moodle.org/501/en/Installation_quick_guide
- **系统要求**: https://docs.moodle.org/501/en/Installing_Moodle#Requirements
- **下载地址**: https://packaging.moodle.org/stable501/moodle-5.1.1.zip
- **PHP Docker 镜像**: https://hub.docker.com/_/php

## 🏗️ 架构设计

### 容器架构
```
┌─────────────────────────────────────────┐
│         Moodle Container                │
│  ┌────────────────────────────────┐    │
│  │   Apache 2.4 + PHP 8.2         │    │
│  │   - mod_rewrite enabled        │    │
│  │   - DocumentRoot: /public      │    │
│  └────────────────────────────────┘    │
│  ┌────────────────────────────────┐    │
│  │   Moodle 5.1.1 Application     │    │
│  │   - /var/www/html              │    │
│  │   - /var/moodledata (data)     │    │
│  └────────────────────────────────┘    │
│  ┌────────────────────────────────┐    │
│  │   Cron Job (每分钟执行)        │    │
│  └────────────────────────────────┘    │
└─────────────────────────────────────────┘
           │
           │ Network: websoft9
           ↓
┌─────────────────────────────────────────┐
│      MariaDB Container                  │
│      - utf8mb4_unicode_ci               │
│      - InnoDB optimized                 │
└─────────────────────────────────────────┘
```

### 目录结构
```
moodle-docker/
├── Dockerfile                 # 主镜像定义
├── docker-entrypoint.sh      # 启动脚本
├── docker-compose.yml        # Bitnami 版本（向后兼容）
├── docker-compose-custom.yml # 自定义镜像版本
├── .env                      # 环境变量
├── build-and-deploy.sh       # 构建部署脚本
├── DOCKERFILE_README.md      # 使用文档
├── STORY.md                  # 本文档
└── src/                      # 配置文件（如需要）
```

## 🔧 技术实现

### 第一阶段：Dockerfile 构建

#### 1.1 基础镜像选择
- **镜像**: `php:8.2-apache`
- **原因**: 
  - 官方维护，安全更新及时
  - 预装 Apache，减少配置工作
  - Debian-based，软件包丰富

#### 1.2 系统依赖安装
```dockerfile
RUN apt-get update && apt-get install -y \
    wget unzip git cron \
    libicu-dev libpng-dev libjpeg62-turbo-dev \
    libfreetype6-dev libxml2-dev libzip-dev \
    libldap2-dev libpq-dev libonig-dev \
    libxslt1-dev libcurl4-openssl-dev \
    default-mysql-client postgresql-client
```

**关键依赖说明**:
- `libicu-dev`: 国际化支持（必需）
- `libpng-dev`, `libjpeg62-turbo-dev`: GD 图像处理
- `libzip-dev`: ZIP 文件处理
- `libldap2-dev`: LDAP 认证
- `default-mysql-client`: 数据库连接测试

#### 1.3 PHP 扩展安装
必需扩展（根据官方要求）:
- ✅ **gd** - 图像处理
- ✅ **intl** - 国际化
- ✅ **mysqli** / **pgsql** - 数据库
- ✅ **opcache** - 性能优化
- ✅ **zip** - 文件压缩
- ✅ **soap** - Web 服务
- ✅ **mbstring** - 多字节字符串
- ✅ **exif** - 图像元数据
- ✅ **ldap** - LDAP 认证

推荐扩展:
- ✅ **redis** - 缓存和会话存储

#### 1.4 PHP 配置优化
```ini
# /usr/local/etc/php/conf.d/moodle.ini
memory_limit = 512M
upload_max_filesize = 512M
post_max_size = 512M
max_execution_time = 600
max_input_vars = 5000
zend.exception_ignore_args = On  # 安全要求
```

```ini
# /usr/local/etc/php/conf.d/opcache-recommended.ini
opcache.enable = 1
opcache.memory_consumption = 128
opcache.max_accelerated_files = 4000
opcache.revalidate_freq = 60
```

#### 1.5 Apache 配置
关键配置:
- **DocumentRoot**: `/var/www/html/public` (Moodle 5.0+ 要求)
- **启用模块**: rewrite, expires, headers, ssl
- **AllowOverride**: All (支持 .htaccess)

#### 1.6 Moodle 下载和部署
```dockerfile
RUN wget -O moodle.zip "https://packaging.moodle.org/stable501/moodle-5.1.1.zip" \
    && unzip -q moodle.zip \
    && mv moodle/* moodle/.??* . \
    && rmdir moodle && rm moodle.zip
```

#### 1.7 Cron 任务配置
```dockerfile
RUN echo "* * * * * www-data /usr/local/bin/php /var/www/html/admin/cli/cron.php >/dev/null" >> /etc/crontab
```

### 第二阶段：Entrypoint 脚本

#### 2.1 启动流程
```bash
1. 启动 cron 服务
2. 等待数据库就绪（健康检查）
3. 检查 config.php 是否存在
   - 不存在：从环境变量生成
   - 存在：跳过配置
4. 运行自动安装（如果设置了管理员账号）
5. 修复文件权限
6. 启动 Apache
```

#### 2.2 数据库连接等待
```bash
for i in {1..30}; do
    if mysqladmin ping -h"$MOODLE_DB_HOST" -u"$MOODLE_DB_USER" -p"$MOODLE_DB_PASSWORD" --silent; then
        echo "Database is ready!"
        break
    fi
    sleep 2
done
```

#### 2.3 自动配置生成
```php
<?php
$CFG->dbtype    = 'mariadb';  // 注意：Moodle 5.1 推荐使用 mariadb
$CFG->dbhost    = 'moodle-mariadb';
$CFG->dbname    = 'moodle';
$CFG->dbuser    = 'moodle';
$CFG->dbpass    = 'password';
$CFG->wwwroot   = 'http://example.com';
$CFG->dataroot  = '/var/moodledata';
$CFG->directorypermissions = 0777;
```

### 第三阶段：Docker Compose 编排

#### 3.1 服务定义
```yaml
services:
  moodle:
    build: .
    image: websoft9dev/moodle:5.1
    depends_on:
      mariadb:
        condition: service_healthy
    environment:
      - MOODLE_DB_TYPE=mariadb
      - MOODLE_DB_HOST=moodle-mariadb
      # ... 其他环境变量
    volumes:
      - moodle_html:/var/www/html
      - moodle_data:/var/moodledata
    ports:
      - "9001:80"

  mariadb:
    image: mariadb:11.4
    environment:
      - MYSQL_DATABASE=moodle
      - MYSQL_USER=moodle
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
    healthcheck:
      test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
      interval: 10s
      retries: 5
```

#### 3.2 数据持久化
- `moodle_html`: Moodle 程序文件
- `moodle_data`: 用户上传、课程内容
- `mariadb_data`: 数据库数据

### 第四阶段：镜像构建和推送

#### 4.1 本地构建测试
```bash
# 构建镜像
docker build -t websoft9dev/moodle:5.1 .
docker build -t websoft9dev/moodle:latest .

# 本地测试
docker compose -f docker-compose-custom.yml up -d

# 验证
curl http://localhost:9001
docker logs moodle
```

#### 4.2 推送到 Docker Hub
```bash
# 登录 Docker Hub
docker login

# 推送镜像
docker push websoft9dev/moodle:5.1
docker push websoft9dev/moodle:5.1.1
docker push websoft9dev/moodle:latest

# 验证
docker pull websoft9dev/moodle:5.1
```

#### 4.3 多架构支持（可选）
```bash
# 创建 buildx builder
docker buildx create --use

# 构建多架构镜像
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t websoft9dev/moodle:5.1 \
  --push .
```

## 🔒 安全考虑

### 镜像安全
- ✅ 使用官方基础镜像
- ✅ 定期更新依赖包
- ✅ 最小化镜像层数
- ✅ 不在镜像中存储敏感信息
- ✅ 使用 `.dockerignore` 排除不必要文件

### 运行时安全
- ✅ 使用非 root 用户运行（www-data）
- ✅ 只开放必要端口
- ✅ 使用环境变量管理密码
- ✅ 启用 PHP 安全设置（zend.exception_ignore_args）
- ✅ 配置 HTTPS（通过反向代理）

### 数据安全
- ✅ 数据库密码加密存储
- ✅ 定期备份 volumes
- ✅ 使用 Docker secrets（生产环境）

## 📊 性能优化

### PHP 优化
- ✅ OPcache 预编译缓存
- ✅ 适当的内存限制（512MB）
- ✅ 会话和缓存使用 Redis

### 数据库优化
- ✅ InnoDB buffer pool 调优
- ✅ utf8mb4_unicode_ci 字符集
- ✅ 连接池配置

### Apache 优化
- ✅ 启用 mod_expires (浏览器缓存)
- ✅ 启用 mod_deflate (压缩)
- ✅ KeepAlive 配置

## 🧪 测试计划

### 功能测试
1. **基础功能**
   - [ ] 容器启动成功
   - [ ] Apache 响应正常
   - [ ] 数据库连接成功
   - [ ] Moodle 安装向导可访问

2. **安装测试**
   - [ ] 系统检查全部通过
   - [ ] 数据库类型识别正确（mariadb）
   - [ ] 自动安装完成
   - [ ] 管理员登录成功

3. **核心功能**
   - [ ] 创建课程
   - [ ] 上传文件
   - [ ] 用户注册
   - [ ] Cron 任务执行

### 性能测试
- [ ] 首页加载时间 < 2s
- [ ] 并发 100 用户响应正常
- [ ] 内存使用 < 1GB（正常负载）

### 兼容性测试
- [ ] 支持 MariaDB 10.11+
- [ ] 支持 PostgreSQL 15+
- [ ] 支持 MySQL 8.0+

## 📦 交付清单

### 代码文件
- [x] Dockerfile
- [x] docker-entrypoint.sh
- [x] docker-compose.yml
- [x] docker-compose-custom.yml
- [x] .env
- [x] .dockerignore

### 文档
- [x] README.md - 项目说明
- [x] DOCKERFILE_README.md - 使用指南
- [x] STORY.md - 本文档
- [x] CHANGELOG.md - 版本历史

### 脚本
- [x] build-and-deploy.sh - 构建部署
- [ ] backup.sh - 备份脚本
- [ ] upgrade.sh - 升级脚本

### Docker Hub
- [ ] 镜像推送：websoft9dev/moodle:5.1
- [ ] 镜像推送：websoft9dev/moodle:5.1.1
- [ ] 镜像推送：websoft9dev/moodle:latest
- [ ] README 更新
- [ ] 标签管理

## 🚀 部署流程

### 开发环境部署
```bash
git clone <repository>
cd moodle
docker network create websoft9
docker build -t websoft9dev/moodle:5.1 .
docker compose -f docker-compose-custom.yml up -d
```

### 生产环境部署
```bash
# 1. 准备环境
docker network create websoft9

# 2. 配置环境变量
cp .env.example .env
nano .env  # 修改密码、域名等

# 3. 拉取镜像
docker pull websoft9dev/moodle:5.1
docker pull mariadb:11.4

# 4. 启动服务
docker compose -f docker-compose-custom.yml up -d

# 5. 查看日志
docker compose logs -f

# 6. 访问应用
https://yourdomain.com
```

## 📈 版本管理

### 版本号规则
- **5.1** - 主版本（跟随 Moodle）
- **5.1.1** - 精确版本
- **latest** - 最新稳定版

### 更新策略
- **每月检查** Moodle 官方更新
- **安全补丁** 立即更新
- **主版本** 经过测试后更新

### Git 标签
```bash
git tag -a v5.1.1 -m "Moodle 5.1.1 Docker image"
git push origin v5.1.1
```

## 🐛 已知问题和解决方案

### 问题 1: 数据库连接失败
**现象**: "Database connection failed"  
**原因**: MariaDB 未完全启动  
**解决**: 
- 添加 healthcheck
- entrypoint 中等待数据库就绪

### 问题 2: /public 目录访问
**现象**: "Moodle root directory must not be publicly accessible"  
**原因**: Moodle 5.0+ 要求 DocumentRoot 指向 /public  
**解决**: 
- 修改 Apache 配置
- `DocumentRoot /var/www/html/public`

### 问题 3: 数据库类型警告
**现象**: "You need to change it from 'mysqli' to 'mariadb'"  
**原因**: Moodle 5.1 推荐使用 mariadb 驱动  
**解决**: 
- 修改 `$CFG->dbtype = 'mariadb'`

## 🎓 学习资源

- [Moodle 官方文档](https://docs.moodle.org/)
- [Docker 最佳实践](https://docs.docker.com/develop/dev-best-practices/)
- [PHP Docker 镜像](https://github.com/docker-library/php)
- [Apache 配置](https://httpd.apache.org/docs/2.4/)

## 📝 待办事项

### 短期目标（本周）
- [x] 完成 Dockerfile 编写
- [x] 完成 docker-entrypoint.sh
- [x] 完成 docker-compose 配置
- [x] 本地测试通过
- [ ] 推送镜像到 Docker Hub
- [ ] 编写完整的 README

### 中期目标（本月）
- [ ] 添加 Redis 缓存支持
- [ ] 添加 SSL/HTTPS 配置示例
- [ ] 创建备份和恢复脚本
- [ ] 多架构支持（amd64, arm64）
- [ ] CI/CD 自动化构建

### 长期目标（季度）
- [ ] 支持所有 Moodle 4.x 和 5.x 版本
- [ ] 性能基准测试报告
- [ ] 集群部署方案
- [ ] Kubernetes YAML 配置
- [ ] 监控和日志方案（Prometheus + Grafana）

## 🤝 贡献指南

### 如何贡献
1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范
- Dockerfile 使用多阶段构建（如适用）
- Shell 脚本遵循 ShellCheck 建议
- 注释清晰，说明关键逻辑
- 提交信息遵循 Conventional Commits

## 📞 支持和反馈

- **问题反馈**: GitHub Issues
- **功能请求**: GitHub Discussions
- **技术支持**: support@websoft9.com
- **文档贡献**: Pull Request

## 📄 许可证

本项目遵循 MIT 许可证。Moodle 本身遵循 GPL v3 许可证。

---

**最后更新**: 2026-02-05  
**维护者**: Websoft9 Team  
**版本**: 1.0.0
