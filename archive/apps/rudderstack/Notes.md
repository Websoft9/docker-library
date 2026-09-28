# RudderStack Notes

## Requirements

- You must obtain a workspace token from RudderStack Cloud (https://app.rudderstack.com/signup)
- Configure the workspace token in the `.env` file before starting the application

## Components

This deployment includes:
- **RudderStack Backend**: The main data plane server (Port: 8080)
- **PostgreSQL**: Database for jobs storage (Port: 5432)
- **Transformer**: Data transformation service (Port: 9090)
- **Metrics Exporter**: Prometheus metrics exporter (Port: 9102)

## Health Check

You can check the health status at: `http://your-server-ip:8080/health`

## FAQ

### How to get workspace token?

1. Sign up at https://app.rudderstack.com/signup
2. Go to Settings > Workspace
3. Copy the workspace token
4. Update `W9_WORKSPACE_TOKEN_SET` in `.env` file

### What ports are used?

- 8080: RudderStack Backend API
- 5432: PostgreSQL Database
- 9090: Transformer Service
- 9102: Metrics Exporter

### How to verify installation?

See official guide: https://www.rudderstack.com/docs/get-started/rudderstack-open-source/sending-test-events/
