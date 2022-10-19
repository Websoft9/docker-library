# MediaWiki

选用 Bitnami 镜像的原因是它可以完成初始化，避免用户上传 配置文件的多余步骤。

## 安装

值得注意的是：MEDIAWIKI_PASSWORD:  有要求（min 10 characters, alphanumeric, no special characters） ，否则容器无法启动（也无法看到[错误信息](https://github.com/bitnami/bitnami-docker-mediawiki/issues/103)）