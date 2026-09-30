# CHANGELOG

## 2026-09-30

- Update Selenium Standalone Chrome to `153.0`.
- Declare the WebDriver API (`4444`) as the `web` surface and the noVNC console (`7900`) as the `admin` surface, with `access.admin.path` set to `/?autoconnect=1&resize=scale`.
- Add `W9_ADMIN_PATH` and `W9_LOGIN_USER` / `W9_LOGIN_PASSWORD` compatibility fields so Websoft9 can render the admin URL and the password.
- Enable the noVNC admin password from the package password through `SE_VNC_PASSWORD`.
- Normalize the package to current conventions: braced `${VAR}` references, documented port purpose, and refreshed upstream metadata.
- Add functional checks for the WebDriver `/status` endpoint and the password-protected noVNC console.
- Document that the noVNC view is black until a WebDriver session starts, and remove stale `src/` files that were never mounted.
