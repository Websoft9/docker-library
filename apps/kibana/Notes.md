# Kibana

- 如果不提前提供 ES 的连接信息，Kibana 可以单独运行
- 配置文件项与环境变量有转换关系(e.g: SERVER_NAME <-> server.name)
- /usr/share/kibana/config/kibana.yml 是主配置文件，启动 Kibana 时没有指定其他配置文件，它将是唯一被使用的配置文件