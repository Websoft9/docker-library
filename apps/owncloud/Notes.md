# Owncloud

OWNCLOUD_DOMAIN 和 OWNCLOUD_TRUSTED_DOMAINS 必须通过环境[变量设置](https://doc.owncloud.com/server/10.13/admin_manual/configuration/server/config_sample_php_parameters.html#define-list-of-trusted-domains-that-users-can-log-into)，config.php 设置它们是无效的。

## FAQ

#### 初始化提示 You are accessing the server from an untrusted domain?

- OWNCLOUD_DOMAIN=${W9_URL}
- OWNCLOUD_TRUSTED_DOMAINS=${W9_URL}

以上两个环境变量都需要设置。OWNCLOUD_TRUSTED_DOMAINS 可以设置多个（以,作为分隔符），OWNCLOUD_TRUSTED_DOMAINS 与 OWNCLOUD_DOMAIN 不一样也不影响访问。

#### 域名发生变化后如何更换 URL ？

原理是上是通过更换 OWNCLOUD_DOMAIN 和 OWNCLOUD_TRUSTED_DOMAINS 后重建应用生效。 当前已经通过 W9_URL_REPLACE=true 实现自动适应。  

#### W9_URL 需要带端口吗？

带或不带都可以，故建议不带