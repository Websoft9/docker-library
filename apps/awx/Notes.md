## AWX

AWX 官方为了用户更灵活的部署，提供了个性化比较强的 [docker 安装方法](https://github.com/ansible/awx/blob/devel/tools/docker-compose)  

它主要包括两个步骤：

1. 构建镜像
2. 利用 Ansible 生成 docker-compose.yml 文件以及其他配置文件

本文档完全是基于ansible官方改造完成