# CHANGELOG

## 2026-10-13
- Updated Elasticsearch community to `9.5.5` (full patch tag, since upstream publishes no `9.5` alias).
- Corrected the access scheme to `http`: the official image serves the REST API as plain HTTP on `9200` (TLS is terminated by the platform), so declaring `https` made the platform expose a broken HTTPS URL.
- Renamed the port variables from `W9_HTTPS_PORT`/`W9_HTTPS_PORT_SET` to `W9_HTTP_PORT`/`W9_HTTP_PORT_SET` to match the actual transport.
- Removed the meaningless `W9_LOGIN_GET_Kibaba_TOKEN` variable and its i18n entry.
- Updated the app test to probe cluster health over HTTP.
- Regenerated the README.

## 2026-09-12
- Replaced the legacy `W9_LOGIN_GET_PASSWORD` usage with the literal `W9_LOGIN_PASSWORD`, because Elasticsearch already controls the initial password directly from `ELASTIC_PASSWORD`.
- Normalized `.env` variable references to the braced `${VAR}` form.
- Regenerated the README.
