# Graylog
## 数据节点(DataNode)
Graylog数据节点是Graylog架构的一个组件，负责管理OpenSearch。此功能允许Graylog管理您的搜索后端，这样您就不必单独安装和管理OpenSearch。
Data Node通过实现证书、管理集群成员资格和促进添加新节点来增强Graylog中数据层的安全性。此外，它还确保安装了正确版本的OpenSearch及其必要的扩展，以使Graylog能够正常运行。

## 安装错误
```
org.graylog2.bootstrap.preflight.PreflightCheckException: /proc/sys/vm/max_map_count value should be at least 262144 but is 65530 (set via "vm.max_map_count" sysctl)
```
原因：Graylog Data Node 在启动时进行了预检查，发现系统的 vm.max_map_count 值低于所需的最小值 262144，导致启动失败。 

解决方法： 

1、打开 /etc/sysctl.conf 文件

2、加入行：vm.max_map_count=262144

3、应用：sudo sysctl -p



## MongoDB 与内核兼容性
MongoDB 8.0.x 在 Linux 内核 6.19 到 7.0.13 之间存在已知不兼容（tcmalloc/rseq 问题），启动时会直接退出，报错：

```
MongoDB cannot start: Linux kernel versions 6.19 and newer has a known incompatibility with this version of MongoDB. See https://jira.mongodb.org/browse/SERVER-121912 for more information.
```

受影响版本：8.0.0 - 8.0.29。8.0.30+ 仍会在内核 6.19 - 7.0.13 上退出。

本包因此将 MongoDB 固定在 7.0（`W9_DB_VERSION=7.0`）。MongoDB 7.0 在所有内核版本上均受支持，且 Graylog 7.1 兼容 MongoDB 7.x - 8.0.x。若后续部署环境内核升级到 7.0.14+ 或 7.1.0+，可再评估升级到 MongoDB 8.0.30+。

## 初始化
Graylog安装完成以后需要进行初始化：

1、到主容器查看用户名和密码，内容大致如下：

========================================================================================================

It seems you are starting Graylog for the first time. To set up a fresh install, a setup interface has

been started. You must log in to it to perform the initial configuration and continue.

Initial configuration is accessible at 0.0.0.0:9000, with username 'admin' and password 'dGFfTTxFiN'.

Try clicking on http://admin:dGFfTTxFiN@0.0.0.0:9000

======================================================================================================== 

2、通过http://Ip:Prot 访问Graylog，输入上一步骤获取的用户和密码后进入初始化页面，安装提示进行初始化即可

3、在未完成初始化前，主容器的状态标识为：unhealthy，初始化完成后自动变成：health

4、初始化完成以后，不要进行“重建”，这样会导致数据节点和Graylog之间的连接验证证书破坏，导致不能连接

## 修改密码
Graylog 的管理员密码由 `GRAYLOG_ROOT_PASSWORD_SHA2` 决定，而前端凭据展示读取的是 `W9_LOGIN_PASSWORD`。两者必须保持一致：

1、生成新密码的 SHA-256：`echo -n '新密码' | sha256sum | awk '{ print $1 }'`

2、同时更新 `.env` 中的 `GRAYLOG_ROOT_PASSWORD_SHA2`（哈希）和 `W9_LOGIN_PASSWORD`（明文）

3、重建应用后生效
