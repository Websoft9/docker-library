# Local overrides

- `create-default-realm.sh` is mounted into `/data/post-setup.d/` so the official Zulip 12.x entrypoint runs it after configuration and database migrations. It creates a default organization plus owner account on first startup.
