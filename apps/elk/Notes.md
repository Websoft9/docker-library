# ELK

ELK 即 Elastic Stack， 它是官方标准的名称。
值得注意的是，ELK 中所有组件的版本必须保持一致（精确到小版本）

> If you are using Elasticsearch 7.16.3, you install Beats 7.16.3, APM Server 7.16.3, Elasticsearch Hadoop 7.16.3, Kibana 7.16.3, and Logstash 7.16.3.

## 安装

1. Elasticsearch 对虚拟内存有[要求](https://www.elastic.co/guide/en/elasticsearch/reference/current/vm-max-map-count.html)
    ```
    sysctl -w vm.max_map_count=262144
    ```

## 账号密码

ES 和 Kibana 可以通过env 设置密码。 Logstash 需手工到 pipeline 中设置密码

## 环境变量

通过配置文件或容器运行时带入均可，配置项与容器环境变量参数的对应关系[参考](https://www.elastic.co/guide/en/logstash/current/docker-config.html#docker-env-config)

## FAQ

#### 启动时间多久？

3-8 分钟

#### Kibana 如何连接 ES？

从8.0之后，需要在 ES 中生产秘钥，方可连接

1. 首先在 ES 中生产密钥对（公钥存放在 elasticsearch/config/service_tokens）

```
# 生成秘钥
docker exec -it elk sh bin/elasticsearch-service-tokens create elastic/kibana test

# 测试秘钥
curl -H "Authorization: Bearer AAEAAWVsYXN0aWMva2liYW5hL3Rlc3Q6bU5CMTVuNEZTdG1BaHBvSWFjVXlHZw" http://47.242.60.114:9200"
```

3. 将私钥通过 kibana 的 ELASTICSEARCH_SERVICEACCOUNTTOKEN 环境变量传入

