# librechat

- LibreChat uses MongoDB as its main database and a pgvector PostgreSQL instance as the vector database for the RAG API.
- MongoDB 8.x refuses to start on Linux kernel 6.19 and newer (MongoDB SERVER-121912), so this package pins `mongo:7.0`, which LibreChat supports. Raise it only after the upstream fix is available.
- The `rag_api` container reads `DB_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` from `.env`; if you point it at an external PostgreSQL, set those values accordingly or the container cannot connect.
- The `admin-panel` service is optional in upstream but is included here; it listens on `W9_ADMIN_GUI_PORT_SET` and needs `ADMIN_PANEL_SESSION_SECRET`.
- `DOMAIN_CLIENT` and `DOMAIN_SERVER` must resolve to the address users actually open, otherwise login and shared links break.

## FAQ

#### Where do uploaded files and generated images live?

They are stored in the `app-uploads`, `app-images`, and `app-data` volumes mounted on the `api` container.

#### How do I add an LLM provider?

Set the provider keys (for example `OPENAI_API_KEY`) in `.env` or configure them in the web interface.
