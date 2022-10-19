## Grafana

* 容器路径：https://grafana.com/docs/grafana/latest/administration/configure-docker/#default-paths
* 容器用户：grafana
* Grafana 默认采用 sqlite，本项目修改为 MySQL
* 集成了：Loki

### 要点

支持 grafana.ini 中的参数作为环境变量，格式：GF_[groupname]_itename，例如：  
   ```
   - GF_SECURITY_ADMIN_USER=${APP_USER}
   - GF_SECURITY_ADMIN_PASSWORD=${APP_PASSWORD}
   ```

### 常见问题

#### 如何为 Grafana 容器默认配置 MySQL 作为后端数据库？

采用类似如下的环境变量
```
GF_DATABASE_URL=mysql://grafana:123456@172.17.0.1:3306/grafana
```

#### 是否可以为 Grafana 设置缓存？

可以