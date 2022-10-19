# GitLab

### 安装

Gitlab 官方提供了一个单体的 Gitlab 镜像，包含应用和数据库等所有组件。

### 端口

Gitlab 最少需要开放两个端口：HTTP 和 SSH 端口，其中 SSH 端口是 git 的一种通道，不是我们常用的 SSH 登录的用途。

### 配置

可以通过GITLAB_OMNIBUS_CONFIG 环境变量传递配置，也可以修改 gitlab.rb 配置文件

### 数据库

* PostgreSQL 内置在 Gitlab 容器中，如何直接连接它？ 暂无方案  
* 是否可以直接修改 gitlab.rb，采用外部数据库？待研究

### 密码

如果启动容器的时不引入密码相关的环境变量，则容器会自动生产一个随机密码。
```
sudo docker exec -it gitlab grep 'Password:' /etc/gitlab/initial_root_password
```

也可以通过 GITLAB_ROOT_PASSWORD 或 gitlab_rails['initial_root_password'] 环境变量预设，但预设方案实操中没有成功。

### 其他

gitlab-runner 是 Gitlab 另外一个工具，类似计划任务。     
