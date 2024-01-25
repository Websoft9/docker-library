# About

- 将数据库脚本所做的一些动作放到了 MySQL 容器
- 当前删除了 onlyoffice-docs, onlyoffice-mailserver

目前启动失败. 做了外挂程序处理（Nginx connection 参数修正）  onlyoffice-docs和onlyoffice-mailserver 可以确认是非必要组件。  

从 [Group](https://github.com/ONLYOFFICE/Docker-CommunityServer/blob/master/docker-compose.groups.yml) 中得知，Onlyoffice Docs 似乎非必须

Group + Email + Docs= Workspace
