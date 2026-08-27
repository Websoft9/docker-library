# Database Contract

Database metadata lives in `apps/<app>/variables.json` under `database`.

Shared defaults live in `metadata/database-defaults.json`.

Platform read path:

1. Read `database.type` from the app.
2. Load the matching type defaults.
3. Merge the app's `database` node over the defaults.
4. Render user-facing database info from the merged result.

Supported modes:

- `bundled`: the compose package includes the database service
- `external`: the user provides an external database, including RDS

Minimal app shape:

```json
{
  "database": {
    "type": "postgresql",
    "supported_modes": ["bundled", "external"],
    "default_mode": "bundled",
    "bundled": {
      "service": "postgres",
      "internal_host": "$W9_ID-postgresql",
      "database_env": "AP_POSTGRES_DATABASE",
      "username_env": "AP_POSTGRES_USERNAME",
      "password_env": "AP_POSTGRES_PASSWORD"
    }
  }
}
```

Rules:

- Keep `W9_DB_EXPOSE` as a coarse compatibility signal.
- Use `database` as the precise machine-readable source.
- `external` covers cloud-managed databases such as RDS.
- App metadata should only override fields that differ from the shared defaults.
