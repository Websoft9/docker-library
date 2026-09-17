# CHANGELOG

## To be released

### Initial Release

- Complete HuggingChat deployment based on official chat-ui project
- MongoDB 8 with replica set for data persistence
- OpenAI-compatible API integration (supports multiple providers)
- Automatic model discovery from configured API endpoint
- Web-based chat interface on port 3000

### Features

- **Multi-Provider Support**: Works with HuggingFace Router, OpenAI, Ollama, llama.cpp, OpenRouter, Azure OpenAI, and more
- **Conversation Management**: Save, organize, and search chat history
- **Custom Assistants**: Create AI assistants with custom instructions and personalities
- **Knowledge Base**: Upload documents for context-aware responses
- **MCP Integration**: Connect to Model Context Protocol servers for extended tools and capabilities
- **LLM Router (Omni)**: Smart model selection based on task requirements
- **Multimodal Support**: Handle text and image inputs (with compatible models)
- **Authentication**: Optional OAuth/OpenID Connect integration
- **Customization**: Configurable app name, branding, and descriptions
- **Usage Limits**: Configurable rate limits and quotas
- **Data Export**: Export conversation data
- **Responsive UI**: Mobile-friendly chat interface
- **Smooth Updates**: Optional client-side message streaming smoothing

### Architecture

- **SvelteKit Frontend**: Modern reactive UI framework
- **MongoDB 8**: Primary database with replica set support
- **OpenAI API Compatibility**: Works with any OpenAI-compatible endpoint
- **Containerized Deployment**: Single-container chat-ui + MongoDB
- **Health Checks**: Automatic MongoDB initialization and readiness checks

### Configuration

- Environment-based configuration via `.env` file
- User-configurable API endpoints and credentials
- Optional advanced features (router, MCP, authentication)
- Websoft9 standard variables (W9_*) for consistency

