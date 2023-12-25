## Kong

Kong OSS 版本包含 Kong Manager 这个管理工具。它的使用有待进一步研究


当然，还有用第三方工具 Konga 作为可视化管理
```
  konga:
    image: pantsel/konga
    container_name: ${W9_ID}
    ports:
      - "${W9_HTTP_PORT_SET}:1337"
    links:
      - kong
    restart: unless-stopped
    environment:
      - NODE_ENV=production
    env_file: .env
```
