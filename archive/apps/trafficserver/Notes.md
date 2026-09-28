# Traffic Server

1. 修改records.yaml以及remap.config  
  remap.config示例：将所有发到该容器的请求反向代理到wordpress容器的80端口
    ```
    map / http://wdpress_nmxmp/
    ```
2. 重建应用

配置文档：https://docs.trafficserver.apache.org/getting-started/index.en.html#configuration