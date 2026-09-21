# Typesense on Docker

## Quick Start

### Deploy Verification

1. In the [Websoft9](https://www.websoft9.com) console, open **My Apps** and select **Typesense**.
2. In the **Access** tab, get the login URL and credentials.
3. Open the login URL in a browser and sign in to confirm the app works.

<!-- W9_GUIDE_START -->
### Usage

Typesense is an HTTP search API server; it has no browser console. In the Websoft9 console, open **My Apps → Typesense → Access** to get the API URL (`http://<host>:8109`).

1. Check the server: `curl http://<host>:8109/health` → `{"ok":true}`.
2. Send the API key from `.env` (`W9_LOGIN_API_KEY`) as the `X-TYPESENSE-API-KEY` header on every other request.

Example: create a collection and search it:

```bash
export TYPESENSE_API_KEY=<W9_LOGIN_API_KEY>
curl -X POST "http://<host>:8109/collections" \
  -H "X-TYPESENSE-API-KEY: ${TYPESENSE_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"name":"books","fields":[{"name":"title","type":"string"}]}'
```

### Change API Key

1. In the Websoft9 console, open the app's **Compose** tab.
2. Update `W9_LOGIN_API_KEY` in `.env` and save.
3. Rebuild the app; the bundled `docsearch-scraper` reads the same key.
<!-- W9_GUIDE_END -->

## Configuration Reference

Websoft9 packages this app from the official [Typesense Docker image](https://hub.docker.com/r/typesense/typesense) and makes some improvements below.

<!-- W9_NOTE_START -->
- Typesense is an HTTP API server; there is no browser admin UI. Authenticate API calls with the `X-TYPESENSE-API-KEY` header set to `W9_LOGIN_API_KEY`.
- `W9_LOGIN_API_KEY` is the admin API key and is also passed to the bundled `docsearch-scraper`.
- Data is persisted in the `typesense` volume (`/data`).
- The bundled `docsearch-scraper` indexes the Websoft9 documentation site by default; edit its `CONFIG` in `docker-compose.yml` to change the target.
<!-- W9_NOTE_END -->

Apps run as containers; rebuild after any configuration change.

### Version Support

Supported versions: 30.2.


### Ports

| Purpose | Port |
| --- | --- |
| Typesense HTTP API | 8108 |


### Data Directory


Data is persisted in the `typesense` volume, mounted at `/data`.


### Environment Variables

Environment variables are defined in the app's `.env` file; see the reference section at the end of `.env` for supported variables.


### Configuration Files


Configuration files live inside the image; mount a single file read-only to override, and never replace the whole directory.


## References

- [Typesense Administrator Guide](https://support.websoft9.com/docs/typesense) by Websoft9

- [Docker Hub image](https://hub.docker.com/r/typesense/typesense)


<!-- W9_TROUBLESHOOT_START -->
## Troubleshooting

**`/health` returns `{"ok":true}` but API calls return 401?**
- Send the `X-TYPESENSE-API-KEY` header with the value of `W9_LOGIN_API_KEY` from `.env`.

**Port not reachable?**
- Confirm `W9_HTTP_PORT_SET` is free and allowed by the firewall / security group.

**Upgrading an existing 29.x instance?**
- v30 auto-migrates synonyms, overrides and analytics rules; take a snapshot before upgrading.
<!-- W9_TROUBLESHOOT_END -->
