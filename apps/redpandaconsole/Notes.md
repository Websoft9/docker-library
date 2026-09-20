# Redpanda Console

Redpanda Console is a web UI for Kafka-compatible clusters. It is a front-end only:
it must be configured with at least one broker, and the broker list is read from
configuration only. The OSS Console cannot start empty and add Kafka from the UI;
changing the cluster means editing `W9_KAFKA_BROKERS_SET` and recreating the container.

## Broker pairing

- `W9_KAFKA_BROKERS_SET` holds the broker address reachable on the `websoft9` network.
- For the Websoft9 Kafka package use the internal listener `kafka:19092`.
  Do not use the external listener (`${W9_URL}:9092`); its advertised address is host-facing.
- If the Kafka app instance is renamed, update `W9_KAFKA_BROKERS_SET` to match.

## Startup behavior

- At least one broker must be configured; an empty `kafka.brokers` fails validation.
- Upstream default is 5 connection retries with backoff, then the process exits with
  code 1. Combined with `restart: unless-stopped` this self-heals once Kafka is up, so
  deploy Kafka first (or expect a short restart loop).
- Do not set `KAFKA_STARTUP_MAXRETRIES=0` (unlimited). In Console v3.12.0 that path hangs
  during startup and Console never begins serving, even when the broker is reachable.

## Schema Registry

- Disabled by default. To enable, set `SCHEMAREGISTRY_ENABLED=true` and point
  `SCHEMAREGISTRY_URLS` at a real Schema Registry service, not at the broker.

## Configuration

- Console v3 reads config from a YAML file or environment variables. Environment keys map
  to the YAML path: `KAFKA_BROKERS` -> `kafka.brokers`, `SCHEMAREGISTRY_URLS` ->
  `schemaRegistry.urls`.
- Reference: https://docs.redpanda.com/current/reference/console/config/

## Authentication

- Authentication and RBAC are enterprise features and are disabled by default.
