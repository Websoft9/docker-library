## AWX

AWX 官方为了用户更灵活的部署，提供了个性化比较强的 [docker 安装方法](ttps://github.com/ansible/awx/tree/22.5.0/tools/docker-compose)  

本文档完全是基于ansible官方改造完成 [docker-compose](https://github.com/ansible/awx/tree/22.5.0/tools/docker-compose)。

它主要包括两个步骤：

1. 构建镜像

![](https://img-1251935913.cos.ap-beijing.myqcloud.com/to/image-20230801004445721.png)

2. 利用 Ansible 生成 docker-compose.yml 文件以及其他配置文件
3. 根据生成的docker-compose改造。

其中一些脚本和配置都是通过 [Makefile](https://github.com/ansible/awx/blob/22.5.0/Makefile))和[bootstrap_development.sh](https://github.com/ansible/awx/blob/22.5.0/tools/docker-compose/bootstrap_development.sh)改造而来的！



启动时记得修改 `.evn`中的DJANGO_SUPERUSER_PASSWORD的值，会自动生成admin管理员的账号密码！

![image-20230801003911132](https://img-1251935913.cos.ap-beijing.myqcloud.com/to/image-20230801003911132.png)
