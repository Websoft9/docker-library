## MongoDB

### MongoDB的认证

MongoDB认证与下列三处相关：
- 环境变量用户和密码的设置，如果设置用户和密码后，默认已经开启了认证
- 通过挂载mongod.conf配置文件设置认证相关选项
- 通过comman参数--noauth或--auth直接设置

 > 优先度：环境变量>command参数>mongod.conf，并且如果环境变量设置了用户密码，comman参数设置成--noauth，无法启动容器


 #### How to get the mantaince version of MongoDB?

 refer to: https://www.mongodb.com/try/download/community
