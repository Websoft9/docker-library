# CHANGELOG

## 2026-10-13

- Updated CodeServer from `4.106.3` to `4.141.0` using the trusted `linuxserver/code-server` image.
- Brought the touched `.env` and `docker-compose.yml` files into current repository policy by converting variable references to `${VAR}` form and adding the required image-env docs block and port-purpose comment.
- Added app-specific validation coverage under `tests/cases.yml` and `tests/check.sh` for the password-protected console login page.
