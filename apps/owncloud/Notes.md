# Owncloud

## FAQ

#### 初始化提示 You are accessing the server from an untrusted domain?

- OWNCLOUD_DOMAIN=${APP_URL}
- OWNCLOUD_TRUSTED_DOMAINS=${APP_URL}

以上两个环境变量都需要设置，且必须保持同样的值

#### APP_URL 需要带端口吗？

带或不带都可以，故建议不带