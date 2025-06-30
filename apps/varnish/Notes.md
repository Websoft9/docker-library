# Varnish

## WordPress 设置 Varnish 教程

1. 分别在 Websoft9 控制台安装 WordPress 和 Varnish 两个应用
   > 确保 Varnish 配置的域名是最终提供给用户访问的域名

2. 编辑 Varnish 应用的 `./src/default.vcl` 文件中相关参数，将 WordPress 容器名和容器端口作为连接点
   ```
    backend default {
        .host = "wordpress_shlez";
        .port = "80";
    }
   ```

3. 重建 Varnish 应用后，Varnish 已经将 WordPress 缓存

4. 访问 Varnish 所绑定的域名，便发现访问速度大大提升 

## 配置选项

- 缓存大小：通过 VARNISH_SIZE 环境变量设置
- 配置文件：`./src/default.vcl`

## FAQ
