## Rocket.Chat

### 连接数据库问题
官方提供了 docker-compose 范例，但连不上数据库，修改 localhost:27017 为 mongo:27017 后可用
```
  mongo-init-replica:
    image: mongo:${APP_DB_MONGODB_VERSION}
    command: 'mongo mongo/rocketchat --eval "rs.initiate({ _id: ''rs01'', members: [ { _id: 0, host: ''mongo:27017'' } ]})"'
    depends_on:
      - mongo
```

已经向官方提交 pull request: https://github.com/RocketChat/Docker.Official.Image/pull/151

### 初始用户以及密码问题

通过wizartd用户自己创建


