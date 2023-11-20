# ERPNext

## Install

官方非常及时的更新了安装所需的镜像，且提供了灵活多变的 docker compose 文件以供用户使用。  

由于过于灵活，导致理解起来有些困难。 实际上 ERPNext 的安装比较简单：

1. 将 example.env 另存为根目录 .env
2. 将 compose.yaml 另存为根目录下 compose.yaml 或 docker-compose.yml，然后略加修改。接下来有两个可选方案：
3. 方案一：使用 compose convert 命令合并多个 compose 为一个完整的 compose 文件（环境变量会替换），然后启动容器
```
docker compose -f compose.yaml -f src/overrides/compose.erpnext.yaml -f src/overrides/compose.redis.yaml -f src/overrides/compose.mariadb.yaml convert > docker-compose.yml
```
4. 方案二（推荐）：启动时引入主 compose 文件以及有选择性的启动 overrides 文件夹下的 docker compose 文件 (多 compose 文件的用法)
```
docker compose -f  docker-compose.yml -f src/overrides/compose.erpnext.yaml -f src/overrides/compose.redis.yaml -f src/overrides/compose.mariadb.yaml up -d
```

5. 主服务 backend 中创建一个 erpnext 项目（此步骤是必须的，但很容易被忽略）
```
W9_URL=8.218.129.87
docker compose exec backend bench new-site youurl --mariadb-root-password yourpassword --admin-password admin123

or

```
参考：https://github1s.com/frappe/frappe_docker/blob/HEAD/docs/site-operations.md

## FAQ

#### 默认管理员账号密码？

username: Administrator  
password: admin

#### ERPNext 镜像与 Frappe 镜像有什么区别？

经过研究，ERPNext 是官方推出的新的镜像，感觉未来应该推荐使用它。

实验中发现 ERPNext  不会出现图片乱码问题

#### 究竟如何部署 ERPNext?

从官方源码中发现，安装文档指南（单一服务器）中对安装写得过于繁琐，但实际上只需采用 overrides 中多个  compose 文件即可快速安装。  

这是怎么回事呢？通过官方的论坛中研究，发现这是文档更新不及时导致，也就是说overrides中的安装在文档中还没有体现，虽然它更具有效率。  


#### 与URL有关的变量有那些？

```
echo "ROUTER=custom-one-example" > ~/gitops/custom-one-example.env
echo "SITES=\`custom-one.example.com\`" >> ~/gitops/custom-one-example.env
echo "BASE_SITE=one.example.com" >> ~/gitops/custom-one-example.env
echo "BENCH_NETWORK=erpnext-one" >> ~/gitops/custom-one-example.env
```

https://github.com/frappe/frappe_docker/blob/main/docs/single-server-example.md#create-custom-domain-to-existing-site