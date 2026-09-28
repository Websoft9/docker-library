# install zulip
## When installing, it is necessary to bind the domain name, otherwise the installation will fail
## After installation, it is necessary to apply for SSL certificate from nginx

## Zulip 12.x packaging
- The package now uses `ghcr.io/zulip/zulip-server:12.2-0`.
- 11.x legacy env names like `DB_HOST` and `SSL_CERTIFICATE_GENERATION` are no longer valid in Zulip 12.x; use `SETTING_*`, `CONFIG_*`, and `CERTIFICATES`.

## First startup organization bootstrap
- The package now creates a default organization and owner account automatically on the first successful startup.
- The organization name, optional subdomain, owner full name, and owner email/password come from `W9_ZULIP_REALM_NAME`, `W9_ZULIP_REALM_STRING_ID`, `W9_ZULIP_ADMIN_FULL_NAME`, `W9_LOGIN_USER`, and `W9_LOGIN_PASSWORD`.
- These values are first-start only; changing them later does not modify an existing Zulip database.
- `SETTING_FAKE_EMAIL_DOMAIN=zulip.example.com` is required because `W9_URL` may resolve to an IP address; Zulip rejects an IP as the fake email domain during owner creation.
- Admin entry is declared as `W9_ADMIN_PATH=/login/`; the app store `access` block mirrors it (web `/`, admin `/login/` on port 443).

## Manual organization creation
```
docker exec -it container_name bash
su zulip -c /home/zulip/deployments/current/manage.py generate_realm_creation_link
```
