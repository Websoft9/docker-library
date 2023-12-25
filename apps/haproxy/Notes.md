## HAProxy

本项目为 Haproxy 本项目增加了一个 haproxy.cfg 配置文件，包含统计和welcome 两个额外的功能。  

> 2.4 版本之后容器用户为 haproxy，之前为 root

### 参考

* [Setting Up Load Balancing by Using HAProxy](https://docs.oracle.com/en/operating-systems/oracle-linux/8/balancing/haproxy-config.html#haproxy-config-roundrobin)

#### FAQs

#### haproxy container failed?

error: Cannot open configuration file/directory /usr/local/etc/haproxy/haproxy.cfg : No such file or directory？

方案： 增加 haproxy.cfg 文件


#### haproxy 的监听是多少？

没有固定的监听端口，用户可以自定义一个或多个

#### 统计功能是全局的吗？

可以全局， 也可以局部。