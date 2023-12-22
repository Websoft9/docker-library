## Grafana

* 容器路径：https://grafana.com/docs/grafana/latest/administration/configure-docker/#default-paths
* 容器用户：grafana
* Grafana 默认采用 sqlite
* 集成了：Loki

### 要点

支持 grafana.ini 中的参数作为环境变量，格式：GF_[groupname]_itename，例如：  
   ```
   - GF_SECURITY_ADMIN_USER=${W9_LOGIN_USER}
   - GF_SECURITY_ADMIN_PASSWORD=${W9_LOGIN_PASSWORD}
   ```

### 常见问题

#### 如何为 Grafana 容器默认配置 MySQL 作为后端数据库？

采用类似如下的环境变量
```
GF_DATABASE_URL=mysql://grafana:123456@172.17.0.1:3306/grafana
```

#### 是否可以为 Grafana 设置缓存？

可以

#### Grafana组合产品

```
version: '3.1'
volumes:
  grafana_data: {}
services:
  influxdb:
    image: influxdb
    restart: always
    environment:
      - PRE_CREATE_DB=cadvisor
    ports:
      - "8086:8086"
    expose:
      - "8090"
      - "8099"
    volumes:
      - ./data/influxdb:/data
  cadvisor:
    image: google/cadvisor
    links:
      - influxdb:influxdb-host
    command: -storage_driver=influxdb -storage_driver_db=cadvisor -storage_driver_host=influxdb-host:8086
    restart: always
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:rw
      - /sys:/sys:ro
      - /var/lib/docker:/var/lib/docker:ro
  grafana:
    user: "104"
    image: grafana/grafana
    restart: always
    links:
      - influxdb:influxdb-host
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/data
    environment:
      - HTTP_USER=admin
      - HTTP_PASS=admin
      - INFLUXDB_HOST=influxdb-host
      - INFLUXDB_PORT=8086
      - INFLUXDB_NAME=cadvisor
      - INFLUXDB_USER=root
      - INFLUXDB_PASS=root
```
