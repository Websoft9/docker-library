## Strapi

- Strapi 5 is packaged here as a prebuilt `websoft9dev/strapi` image because upstream no longer publishes official container images.
- The package now targets fresh Strapi 5 deployments; existing Strapi 3 volumes or databases are not directly upgrade-compatible.
- The first administrator is seeded during the initial boot only, using `W9_LOGIN_USER` and `W9_LOGIN_PASSWORD`.
- The database is chosen at runtime by `config/database.js` from `DATABASE_CLIENT`; SQLite is the default and PostgreSQL/MySQL are external-only options. The `pg` and `mysql2` drivers are preinstalled in the image.
- The external database must be empty on first start; the bundled SQLite file is not migrated into it automatically.
