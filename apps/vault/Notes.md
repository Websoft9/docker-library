# Vault

Vault 是hashicorp旗下的密码管理方案，支出多用户户、API和LDAP等。 

## 安装

Vault 默认启动（cmd 不带任何参数）是以 Dev  模式运行。Dev 模式下只需要通过 Vault 容器日志查看启封后的结果 **Root Token**。

## GUI

默认支持图形化界面（端口：8200），且图形化界面可以很方面的运行 CLI。

## 配置文件

支持通过环境变量导入配置文件的参数