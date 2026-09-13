# Open WebUI

## Guide

### Quick Start

1. Create the administrator credential on first sign-up.
2. Go to **Settings > Admin Settings** to add an LLM provider, e.g. [tinydolphin](https://ollama.com/library/tinydolphin) which does not exceed 1GB.
3. Select the model for chat.

### Optional local AI containers

`ollama` and `chroma` are optional Docker Compose profiles and are **not started by default**:

- `ollama`: local LLM runtime. Start it with `docker compose --profile ollama up -d`, then pull a model with `docker exec <app>-ollama ollama pull <model>`.
- `chroma`: external vector database for RAG. Start it with `docker compose --profile chroma up -d`, then set `CHROMA_HTTP_HOST=${W9_ID}-chroma` and `CHROMA_HTTP_PORT=8000` in `.env` and rebuild the app.

Neither profile publishes host ports; both are reachable only on the `websoft9` network.

### GPU / CUDA

Open WebUI also publishes CUDA image tags (for example `cuda` and `v0.11.3-cuda`) for NVIDIA GPU hosts. This package does not use the CUDA variant; GPU support is out of scope here.

### Config

- Ollama URL: **Settings > Admin Settings > Connections**
- Multiple languages: yes

## FAQ
