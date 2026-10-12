## Kong

- Upstream docs now live in `variables.json > upstream` instead of compose-file comments.
- `web` access points to Kong Manager at `http://${W9_URL}${W9_ADMIN_PATH}`; the proxy listener on port 8000 is modeled as an additional `admin` surface for operators who want a direct browser/API entry.
- This package uses PostgreSQL-backed mode, so `.env` declares `KONG_DATABASE=postgres` explicitly rather than relying on image defaults.
- Removed the unused `kong_prefix_vol`; only the tmpfs mount at `/tmp` is active in the current package layout.
