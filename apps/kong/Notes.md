## Kong

- Upstream docs now live in `variables.json > upstream` instead of compose-file comments.
- Kong Manager (`admin`, port 8002) is the default web entry. The proxy (`gateway`, port 8000) and Admin API (`api`, port 8001) are separate port groups with independent bindings.
- This package uses PostgreSQL-backed mode, so `.env` declares `KONG_DATABASE=postgres` explicitly rather than relying on image defaults.
- Removed the unused `kong_prefix_vol`; only the tmpfs mount at `/tmp` is active in the current package layout.
