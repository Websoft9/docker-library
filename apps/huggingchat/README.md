# HuggingChat on Docker  

This is a **[Docker Compose template](https://github.com/Websoft9/docker-library)** powered by [Websoft9](https://www.websoft9.com) based on Docker for HuggingChat (chat-ui):

- community: latest

## About HuggingChat

HuggingChat is an open-source web UI for chatting with AI models. It's the same interface that powers [huggingface.co/chat](https://huggingface.co/chat). This deployment uses the official [chat-ui](https://github.com/huggingface/chat-ui) project from Hugging Face.

## System Requirements

The following are the minimal recommended requirements:

* **RAM**: 4 GB or more
* **CPU**: 2 cores or higher
* **Disk**: at least 10 GB of free space
* **bandwidth**: more fluent experience over 100M  

## Prerequisites

Before deploying HuggingChat, you **must** have:

1. **OpenAI-compatible API Access**: Credentials for at least one of:
   - **Hugging Face Token** (recommended) - Get from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   - OpenAI API key
   - Ollama running locally
   - llama.cpp server
   - OpenRouter account
   - Azure OpenAI credentials
   - Any other OpenAI-compatible endpoint

## Install

You can install HuggingChat by following [How to use it?](https://github.com/Websoft9/docker-library#how-to-use-it).   

### Quick Start Configuration

1. **Edit environment variables** in `.env` file before deployment:
   ```bash
   # For Hugging Face Router (recommended)
   W9_OPENAI_BASE_URL_SET=https://router.huggingface.co/v1
   W9_OPENAI_API_KEY_SET=hf_your_token_here
   
   # Or for OpenAI
   W9_OPENAI_BASE_URL_SET=https://api.openai.com/v1
   W9_OPENAI_API_KEY_SET=sk-your-openai-key
   
   # Or for local Ollama
   W9_OPENAI_BASE_URL_SET=http://host.docker.internal:11434/v1
   W9_OPENAI_API_KEY_SET=ollama
   ```

2. **Deploy the stack**:
   ```bash
   docker compose up -d
   ```

3. **Wait for MongoDB initialization** (about 30 seconds for replica set setup)

4. **Access the web interface**: 
   - URL: `http://your-server-ip:9001`
   - Start chatting immediately (no login required by default)

## Architecture

HuggingChat includes:

- **MongoDB 8**: Database with replica set for conversations and user data
- **Chat UI**: SvelteKit-based web interface
- **API Integration**: Connects to your chosen OpenAI-compatible endpoint
- **Automatic Model Discovery**: Fetches available models from API

## Features

### Core Features
- 💬 Multi-model chat interface
- 📚 Conversation history management
- 🤖 Custom assistant creation
- 📄 Document upload for knowledge base
- 🔧 MCP tools integration
- 🎯 Smart model routing (Omni)
- 🖼️ Multimodal support (text + images)

### Optional Features
- 🔐 OAuth/OpenID authentication
- 📊 Usage limits and quotas
- 📈 Analytics integration
- 🎨 Custom branding
- 📤 Data export capabilities

## Configuration Examples

### Using Hugging Face Router
```env
W9_OPENAI_BASE_URL_SET=https://router.huggingface.co/v1
W9_OPENAI_API_KEY_SET=hf_xxxxxxxxxxxxxxxxxxxxx
```

### Using OpenAI
```env
W9_OPENAI_BASE_URL_SET=https://api.openai.com/v1
W9_OPENAI_API_KEY_SET=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

### Using Local Ollama
```env
W9_OPENAI_BASE_URL_SET=http://host.docker.internal:11434/v1
W9_OPENAI_API_KEY_SET=ollama
```

### Custom Branding
```env
W9_APP_NAME_SET=MyAI Chat
PUBLIC_APP_DESCRIPTION=Your custom AI chat platform
```

## Advanced Configuration

For advanced features like authentication, LLM router, MCP servers, and more, edit the additional environment variables in the `.env` file. See [Notes.md](./Notes.md) for detailed configuration guides.

## Documentation

- [HuggingChat Official Repository](https://github.com/huggingface/chat-ui)
- [Websoft9 Documentation](https://support.websoft9.com)

## Notes

- MongoDB replica set initialization takes ~30 seconds on first start
- All chat history is persisted in MongoDB volumes
- Models are fetched automatically from configured API endpoint
- For production use, configure authentication and usage limits
- SSL/HTTPS can be configured through Websoft9's Nginx Proxy Manager