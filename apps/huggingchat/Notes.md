# HuggingChat

## Prerequisites

### Required Configuration

Before using HuggingChat, you **must** configure an OpenAI-compatible API endpoint:

1. **API Configuration** (via environment variables):
   - `W9_OPENAI_BASE_URL_SET`: Base URL of your OpenAI-compatible API
   - `W9_OPENAI_API_KEY_SET`: API key for authentication

### Supported API Providers

HuggingChat works with any OpenAI-compatible API:

- **Hugging Face Router**: `https://router.huggingface.co/v1` (recommended)
  - Use your Hugging Face token as API key (starts with `hf_`)
  - Access to multiple open-source models
  
- **OpenAI**: `https://api.openai.com/v1`
  - Use your OpenAI API key
  
- **Ollama**: `http://your-ollama-host:11434/v1`
  - Run local models
  - API key can be any string (Ollama ignores it)
  
- **llama.cpp Server**: `http://your-server:8080/v1`
  - Local model deployment
  - API key can be any string
  
- **OpenRouter**: `https://openrouter.ai/api/v1`
  - Access to multiple model providers
  
- **Azure OpenAI**: Your Azure endpoint
  - Use your Azure API key

## Features

- **Multi-model Support**: Automatically fetches available models from configured API
- **Conversation Management**: Save and organize chat sessions
- **Assistant Creation**: Build custom AI assistants with specific instructions
- **Knowledge Base**: Upload documents for context-aware conversations
- **MCP Tools**: Integrate Model Context Protocol servers for extended functionality
- **LLM Router (Omni)**: Smart routing to best model based on task
- **Authentication**: Optional OAuth/OpenID integration
- **Customizable**: Brand with your own name, logo, and description

## FAQ

### How to access HuggingChat?

After deployment, access the web interface at: `http://your-server-ip:9001`

### How to configure API credentials?

1. Go to application environment variables
2. Set `W9_OPENAI_BASE_URL_SET` to your API endpoint
3. Set `W9_OPENAI_API_KEY_SET` to your API key
4. Restart the application

For Hugging Face Router:
- Get your token from: https://huggingface.co/settings/tokens
- Use token as `W9_OPENAI_API_KEY_SET=hf_your_token_here`

### How to use local models with Ollama?

1. Install Ollama on your server
2. Set `W9_OPENAI_BASE_URL_SET=http://host.docker.internal:11434/v1`
3. Set `W9_OPENAI_API_KEY_SET=ollama` (any value works)
4. Restart the application

### How to enable authentication?

Configure OpenID/OAuth in environment variables:
```
OPENID_PROVIDER_URL=https://huggingface.co
OPENID_CLIENT_ID=your_client_id
OPENID_CLIENT_SECRET=your_client_secret
AUTOMATIC_LOGIN=true
```

### What is the Omni (LLM Router) feature?

Omni is a smart routing system that:
- Analyzes each user message
- Selects the best model for the task
- Routes multimodal requests to vision-capable models
- Routes tool-calling requests to function-capable models

To enable, configure `LLM_ROUTER_*` variables.

### How to add MCP (Model Context Protocol) servers?

Configure in environment variables:
```
MCP_SERVERS=[{"name": "Web Search", "url": "https://mcp.exa.ai/mcp"}]
MCP_FORWARD_HF_USER_TOKEN=true
```

Users can also add custom MCP servers through the UI.

### How to customize branding?

Set these environment variables:
- `W9_APP_NAME_SET`: Your app name
- `PUBLIC_APP_DESCRIPTION`: App description
- `PUBLIC_APP_ASSETS`: Set to "chatui" or "huggingchat"

### Minimum system requirements?

- CPU: 2 cores
- Memory: 4 GB
- Disk: 10 GB
- MongoDB is included and configured automatically

### How to backup data?

Backup the MongoDB volume:
```bash
docker volume inspect huggingchat-mongodb_data
```

All conversations, users, and settings are stored in MongoDB.

### Troubleshooting

**"No models available" error:**
- Verify `W9_OPENAI_BASE_URL_SET` is correct
- Check `W9_OPENAI_API_KEY_SET` is valid
- Ensure the API endpoint is accessible from the container
- Test: `curl ${OPENAI_BASE_URL}/models -H "Authorization: Bearer ${OPENAI_API_KEY}"`

**MongoDB connection error:**
- Wait 30 seconds for MongoDB replica set initialization
- Check logs: `docker logs huggingchat-mongodb`
- Ensure MongoDB healthcheck passes

**Authentication not working:**
- Verify OAuth client ID and secret
- Check redirect URLs in OAuth provider settings
- Enable `AUTOMATIC_LOGIN=true` to require login

**Performance issues:**
- Increase MongoDB memory limits
- Check API provider rate limits
- Monitor container resources: `docker stats`
