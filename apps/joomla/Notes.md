## Joomla

本项目采用 Joomla 官方镜像，经过研究发现其特点如下：

* 即使给 joomla 容器配置数据库，它不支持数据库直接连接（即无法跳过安装向导的数据库配置页面）
* joomla 容器的数据库环境变量虽然无法实现免数据库连接，但又必不可少
* /var/www/html 不支持 bind mount 挂载，即使权限设置777， 也不可以

故，最后采用 Bitnami 的镜像