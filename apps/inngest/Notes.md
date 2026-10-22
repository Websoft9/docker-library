# Inngest

## Notes

- `INNGEST_EVENT_KEY` and `INNGEST_SIGNING_KEY` protect event ingestion and app sync. Change them from the packaged defaults before production use.
- The signing key must be a valid hexadecimal string with an even number of characters (`openssl rand -hex 32`).
- PostgreSQL stores system data and run history; Redis holds the queue and run state. Back up both volumes before upgrades.
