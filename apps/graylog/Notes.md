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
