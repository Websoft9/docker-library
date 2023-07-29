## AWX

AWX 官方为了用户更灵活的部署，提供了个性化比较强的 [docker 安装方法](https://github.com/ansible/awx/blob/devel/tools/docker-compose)  

它主要包括两个步骤：

1. 构建镜像
2. 利用 Ansible 生成 docker-compose.yml 文件以及其他配置文件

最后通过 docker-compose 运行项目。

基于这个原理，我们直接将以上过程产生的结果进行了简化处理，而从产生了此项目


## 第一次运行需要执行迁移命令
```shell
docker exec -ti awx_task awx-manage migrate
```

## 创建管理员账号密码
```shell
docker exec -ti awx_web awx-manage createsuperuser
```