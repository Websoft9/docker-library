# Kafka

This package runs a single-node Apache Kafka in KRaft mode (one process acting as both
broker and controller) using the official `apache/kafka` image. ZooKeeper is not used.

## Client access

- In-cluster clients connect to `kafka:19092` (`PLAINTEXT`).
- External clients connect to `${KAFKA_ADVERTISED_HOST}:${W9_MQ_PORT_SET}` (`PLAINTEXT_HOST`).
- `KAFKA_ADVERTISED_HOST` defaults to `localhost`. Set it to the server IP or domain
  so remote clients can reach the broker.
- Advertised listeners are read once at broker startup, so changing
  `KAFKA_ADVERTISED_HOST` requires recreating the container.

### Do not declare W9_URL here

Kafka is not a web app and must **not** declare `W9_URL` or `W9_URL_REPLACE`.
The Websoft9 platform treats any app with `W9_URL` as a web app: it rewrites `W9_URL`
and then tries to create an nginx proxy using `W9_HTTP_PORT` / `W9_HTTPS_PORT`.
Kafka has neither, so declaring `W9_URL` makes the platform fail during install with
`Initialize repo error`. Use `KAFKA_ADVERTISED_HOST` instead.

## Running a 3-node cluster

The single-node package is not a cluster. The upstream reference for a 3-node KRaft
cluster is:

- https://github.com/apache/kafka/blob/trunk/docker/examples/docker-compose-files/cluster/combined/plaintext/docker-compose.yml

Differences from this package:

- one service per node (`kafka-1`, `kafka-2`, `kafka-3`), each with a unique
  `KAFKA_NODE_ID`, `hostname`, and data volume
- `KAFKA_CONTROLLER_QUORUM_VOTERS=1@kafka-1:9093,2@kafka-2:9093,3@kafka-3:9093`
- per-node `KAFKA_ADVERTISED_LISTENERS` using that node's hostname
- the same `CLUSTER_ID` on every node
- replication raised to 3 and ISR to 2:
  `KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=3`,
  `KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR=3`,
  `KAFKA_SHARE_COORDINATOR_STATE_TOPIC_REPLICATION_FACTOR=3`,
  `KAFKA_TRANSACTION_STATE_LOG_MIN_ISR=2`,
  `KAFKA_SHARE_COORDINATOR_STATE_TOPIC_MIN_ISR=2`

This package already parameterizes the cluster-relevant values through
`KAFKA_NODE_ID`, `KAFKA_CONTROLLER_QUORUM_VOTERS`, and `KAFKA_ADVERTISED_LISTENERS`
(referencing `${W9_ID}`, `${KAFKA_ADVERTISED_HOST}`, and `${W9_MQ_PORT_SET}`), so a cluster file can
reuse the same conventions.

## Operational notes

- Persistence lives in the `kafka_data` volume mounted at `/var/lib/kafka/data`.
- `CLUSTER_ID` identifies the KRaft cluster; keep it stable across restarts.
- The healthcheck runs `kafka-broker-api-versions.sh` against `localhost:9092`.
