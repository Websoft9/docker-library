# Coze Studio

## Configuration Requirements

### Required Configuration

Before using Coze Studio, you **must** configure at least one AI model provider:

1. **For Agent & Workflow**: Configure the model settings via environment variables:
   - `W9_MODEL_PROTOCOL_SET`: Model protocol (e.g., "ark", "openai", "ollama")
   - `W9_MODEL_NAME_SET`: Display name for the model
   - `W9_MODEL_ID_SET`: Model ID for API calls
   - `W9_MODEL_API_KEY_SET`: API key for authentication
   - `W9_MODEL_BASE_URL_SET`: Base URL for the model API

2. **For Knowledge Base (Embedding)**: Configure embedding settings:
   - `EMBEDDING_TYPE`: Type of embedding provider (ark/openai/ollama/gemini)
   - Provider-specific settings (API key, base URL, model name, dimensions)

### Supported Model Providers

- **Ark (ByteDance/Volcengine)**: Recommended for best compatibility
- **OpenAI**: Including Azure OpenAI
- **Ollama**: For local model deployment
- **Gemini**: Google's AI models
- **DeepSeek**: Alternative AI provider
- **Qwen**: Alibaba's AI models

## FAQ

### How to access Coze Studio?

After deployment, access the web interface at: `http://your-server-ip:9001`

### How to configure models?

1. Go to the application environment variables
2. Update the model configuration variables (W9_MODEL_*)
3. Restart the application

### What are the minimum system requirements?

- CPU: 4 cores
- Memory: 8 GB
- Disk: 20 GB
- Recommended: 8 cores, 16 GB memory for production use

### How to enable SSL/HTTPS?

Configure through Websoft9's proxy manager (Nginx Proxy Manager).

### How to backup data?

Backup the following Docker volumes:
- mysql_data
- redis_data
- elasticsearch_data
- minio_data
- etcd_data
- milvus_data

### Troubleshooting

**Service not starting:**
- Check if all required environment variables are configured
- Verify Docker has enough resources allocated
- Check logs: `docker logs coze-server`

**Knowledge base not working:**
- Ensure embedding configuration is properly set
- Verify the embedding API key is valid
- Check Milvus and Elasticsearch are running

**Model not responding:**
- Verify model API key and base URL
- Check network connectivity to model provider
- Review server logs for error messages
