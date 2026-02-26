# src/ Configuration Files

This folder contains configuration files mounted into the Debezium Server container.

## Files

| File | Container Path | Purpose |
|------|---------------|---------|
| `application.properties` | `/debezium/config/application.properties` | Main Debezium Server config: source connector, sink, logging |

## Usage

1. Edit `application.properties` to set your source database and sink target
2. Change `debezium.source.connector.class` for your database type
3. Set database credentials (`database.hostname`, `database.user`, `database.password`)
4. Set sink URL (`debezium.sink.http.url`) or switch to another sink type
5. Run `docker compose up -d` (changes take effect on restart)

## References

- Configuration reference: https://debezium.io/documentation/reference/stable/operations/debezium-server.html
- Connector list: https://debezium.io/documentation/reference/stable/connectors/
