## HAProxy

to do:  init password

### 注意

* 2.4 版本之后容器用户为 haproxy，之前为 root

* 本项目增加了一个 samples/haproxy.cfg 模板文件

### 参考

* [Setting Up Load Balancing by Using HAProxy](https://docs.oracle.com/en/operating-systems/oracle-linux/8/balancing/haproxy-config.html#haproxy-config-roundrobin)

#### FAQs

#### haproxy container failed?

error: Cannot open configuration file/directory /usr/local/etc/haproxy/haproxy.cfg : No such file or directory？

方案： 增加 haproxy.cfg 文件