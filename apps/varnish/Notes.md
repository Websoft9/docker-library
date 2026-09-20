# Varnish

## WordPress 设置 Varnish 教程

1. 分别在 Websoft9 控制台安装 WordPress 和 Varnish 两个应用
   > 确保 Varnish 配置的域名是最终提供给用户访问的域名

2. 编辑 Varnish 应用的 `.env` 文件，通过 `VARNISH_BACKEND_HOST` 将后端指向 WordPress 容器
   ```
   VARNISH_BACKEND_HOST=http://wordpress_shlez:80/
   ```

3. 重建 Varnish 应用后，Varnish 已经将 WordPress 缓存

4. 访问 Varnish 所绑定的域名，便发现访问速度大大提升

## Varnish 禁止爬虫访问

1. 编辑 Varnish 应用的 `./src/default.vcl` 文件，在 `sub vcl_recv` 中增加如下内容，其中 `Sogou web spider` 改成你想要禁用的爬虫名：
   ```
   sub vcl_recv {
       if (req.http.user-agent ~ "Sogou web spider") {
           return (synth(403, "Forbidden"));
       }
   }
   ```

2. 重建 Varnish 应用后，Varnish 已经对爬虫禁用

## 配置选项

- 缓存大小：通过 `VARNISH_SIZE` 环境变量设置
- 后端地址：通过 `VARNISH_BACKEND_HOST` 环境变量设置（未设置时提供一个本地占位页面）
- 文件服务模式：设置 `VARNISH_FILESERVER=true` 后，Varnish 直接提供 `/var/www/html` 下的静态文件
- 配置文件：`./src/default.vcl`，可自定义 VCL 规则

## FAQ
