# About

This folder includes configuration files mounted to containers and used by Websoft9 SigNoz deployment.

## Directory Structure

- `clickhouse/`: ClickHouse database configuration files
  - `config.xml`: Main ClickHouse configuration
  - `users.xml`: User and access control settings
  - `custom-function.xml`: Custom function definitions
  - `cluster.xml`: Cluster configuration
  - `user_scripts/`: Custom scripts for ClickHouse
  
- `signoz/`: SigNoz application configuration
  - `prometheus.yml`: Prometheus configuration
  - `otel-collector-opamp-config.yaml`: OpenTelemetry collector OpAMP configuration
  
- `dashboards/`: Custom dashboard definitions (JSON files)

- `otel-collector-config.yaml`: OpenTelemetry Collector main configuration

## Configuration Files Source

All configuration files are synced from the official SigNoz repository:
https://github.com/SigNoz/signoz/tree/main/deploy/common

## Customization

You can customize these configuration files according to your needs. Please refer to the official documentation:
- SigNoz: https://signoz.io/docs/
- ClickHouse: https://clickhouse.com/docs/
- OpenTelemetry: https://opentelemetry.io/docs/
