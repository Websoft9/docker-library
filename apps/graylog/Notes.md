# Graylog

## URL

Graylog 是前后端分离的系统，我们访问的 Web 界面是通过 API 与后端交互。

Graylog 有如下几个 URL/URI，它们都是 HTTP API 的设置

* http_bind_address 是 Graylog HTTP API 监听的网址，建议设置为：0.0.0.0:9000
* http_publish_uri 是集群内部使用的 URL，默认为：http://$http_bind_address/
* http_external_uri 是外部访问的URL，默认为为： $http_publish_uri

以上理解还无法形成通俗易懂的逻辑关系，有待进一步学习

## FAQ

#### 如何访问 API？

https://Internet IP:9000/api/api-browser/global/index.html

#### 管理员密码怎么设置？
运行 echo -n 'admin' | sha256sum | awk '{ print $1 }' 命令，得到密文后传递给容器
