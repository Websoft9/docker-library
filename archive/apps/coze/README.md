# Coze Studio on Docker  

This is a **[Docker Compose template](https://github.com/Websoft9/docker-library)** powered by [Websoft9](https://www.websoft9.com) based on Docker for Coze Studio:

- community: latest

## System Requirements

The following are the minimal recommended requirements:

* **RAM**: 8 GB or more (16 GB recommended for production)
* **CPU**: 4 cores or higher (8 cores recommended for production)
* **Disk**: at least 20 GB of free space
* **bandwidth**: more fluent experience over 100M  

## Prerequisites

Before deploying Coze Studio, you **must** have:

1. **AI Model Provider Access**: API credentials for at least one AI model provider:
   - Ark (ByteDance/Volcengine) - Recommended
   - OpenAI or Azure OpenAI
   - Ollama (for local deployment)
   - Google Gemini
   - DeepSeek, Qwen, or other compatible providers

2. **Embedding Model**: For knowledge base functionality, configure embedding settings with proper API credentials

## Install

You can install Coze Studio by following [How to use it?](https://github.com/Websoft9/docker-library#how-to-use-it).   

### Configuration Steps

1. **Edit environment variables** in `.env` file before first deployment:
   ```bash
   # Required: Configure your AI model
   W9_MODEL_PROTOCOL_SET="ark"           # or "openai", "ollama", etc.
   W9_MODEL_NAME_SET="your-model-name"
   W9_MODEL_ID_SET="your-model-id"
   W9_MODEL_API_KEY_SET="your-api-key"
   W9_MODEL_BASE_URL_SET="https://api.example.com"
   
   # Required: Configure embedding for knowledge base
   EMBEDDING_TYPE="ark"
   ARK_EMBEDDING_BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
   ARK_EMBEDDING_MODEL="your-embedding-model"
   ARK_EMBEDDING_API_KEY="your-embedding-api-key"
   ```

2. **Deploy the stack**:
   ```bash
   docker compose up -d
   ```

3. **Access the web interface**: 
   - URL: `http://your-server-ip:9001`
   - Initial setup will guide you through the configuration

## Architecture

Coze Studio includes the following services:

- **MySQL 8.4.5**: Primary database
- **Redis 8.0**: Caching and session storage
- **Elasticsearch 8.18.0**: Full-text search engine
- **MinIO**: Object storage for files and media
- **Milvus v2.5.10**: Vector database for knowledge base
- **Etcd**: Distributed configuration
- **NSQ**: Message queue system
- **Coze Server**: Backend API service
- **Coze Web**: Frontend web interface

## Documentation

[Coze Studio Official Documentation](https://github.com/coze-dev/coze-studio)

For Websoft9 support and additional guides, visit [Websoft9 Documentation](https://support.websoft9.com)

## Notes

- All data is persisted in Docker volumes
- Ensure adequate resources are allocated to Docker
- For production use, configure proper backup strategies for all volumes
- SSL/HTTPS can be configured through Websoft9's Nginx Proxy Manager
