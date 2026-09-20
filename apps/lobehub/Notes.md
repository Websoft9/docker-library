# LobeHub

LobeHub (formerly LobeChat) is a self-hosted AI workspace. This package runs the server deployment model with bundled PostgreSQL, Redis and S3-compatible object storage (RustFS).

## Use case

### Use Self-hosting LLM

You can create one Ollama application at **Websoft9 AppStore** or prepare an online Ollama service, then start to setup it:

1. Set your ollama service URL from **设置 > 语言模型 > Ollama**

2. Select ollama LLM at your Chat interface

3. When you starting chat, it remind download the LLM model

4. After download, you can chat now

## Config

- Multiple languages: 跟随系统
- Multiple LLM: Yes
- Self-hosting LLM: Integrated ollama

## FAQ

#### How to set LLM keys?

Both can set them at `.env` or client interface

#### Where is uploaded data stored?

Files and images are stored in the bundled RustFS (S3-compatible) service; its data lives in the `rustfs_data` volume.
