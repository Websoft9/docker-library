## Guacamole

通过web实现无客户端连接远程图形化桌面

#### 架构图

![image](https://user-images.githubusercontent.com/43192516/162340032-d8e89974-d5b0-4ab7-97a1-f1509588850e.png)


Guacamole是一个tomcat实现的web程序，它本身不了解vnc，rdp协议，它和guacd通过用自己的协议通信。guacd 才是 Guacamole 的核心，guacd 也不理解任何特定的远程桌面协议。但是它接受web端连接请求，通过加载插件来实现远程连接。

#### 其他

为了让Guacamole正常运行，需要通过guacamole容器生成初始postgres数据；并将此文件挂载到postgres容器；通过研究，加深了对ENTRYPOINT和CMD的理解，以下几种方式都可以达到同样效果：

```
entrypoint: [ "bash", "-c", "chmod -R +x /opt/guacamole/init && /opt/guacamole/bin/initdb.sh --postgres > /opt/guacamole/init/initdb.sql"]
command: [ "bash", "-c", "chmod -R +x /opt/guacamole/init && /opt/guacamole/bin/initdb.sh --postgres > /opt/guacamole/init/initdb.sql"]

```


