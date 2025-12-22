# Coze Studio

## Configuration Requirements

### Required Configuration

在使用coze之前，你需要提供至少一个AI模型供应商:

1. **适用于代理和工作流**：通过环境变量配置模型设置：
   - `W9_MODEL_PROTOCOL_SET`: 模型协议 (如： "ark", "openai", "ollama")
   - `W9_MODEL_NAME_SET`: 模型显示名称
   - `W9_MODEL_ID_SET`: 用于 API 调用的模型 ID
   - `W9_MODEL_API_KEY_SET`: 用于认证的 API 密钥
   - `W9_MODEL_BASE_URL_SET`: 模型 API 的基础 URL  
      (以上配置在安装前会被要求输入，并且代入到以下配置：)
      ```
      MODEL_PROTOCOL_0="${W9_MODEL_PROTOCOL_SET:-ark}"
      MODEL_OPENCOZE_ID_0="100001"
      MODEL_NAME_0="${W9_MODEL_NAME_SET:-}"
      MODEL_ID_0="${W9_MODEL_ID_SET:-}"
      MODEL_API_KEY_0="${W9_MODEL_API_KEY_SET:-}"
      MODEL_BASE_URL_0="${W9_MODEL_BASE_URL_SET:-}"
      ```
      (你可以通过复制并修改后面的数字以及内容来配置多个模型)
   

2. **用于知识库（嵌入）**：配置嵌入设置：
   - `EMBEDDING_TYPE`: 嵌入提供商类型 (ark/openai/ollama/gemini)
   - 特定于提供商的设置 (API key, base URL, model name, dimensions)

### 支持的模型提供商

- **Ark (ByteDance/Volcengine)**: 推荐以获得最佳兼容性
- **OpenAI**: 包括 Azure OpenAI
- **Ollama**: 用于本地模型部署
- **Gemini**: 谷歌的人工智能模型
- **DeepSeek**
- **Qwen**: 阿里巴巴的AI模型

## FAQ


### 怎么配置模型?

1. 在应用页面点击编排-马上修改，进入.env文件
2. 修改模型配置相关变量 (W9_MODEL_*)
3. 重建应用

### 故障排查

**服务没有启动:**
- 检查所有必需的环境变量是否已配置
- 验证 Docker 是否分配了足够的资源
- 检查日志: `docker logs coze_{ID}-server`

**知识库无法使用:**
- 确保嵌入配置设置正确
- 验证嵌入式 API 密钥是否有效
- 检查 Milvus 和 Elasticsearch 是否正在运行

**模型无响应:**
- 验证模型 API 密钥和基础 URL
- 检查与模型提供商的网络连接
- 查看服务器日志中的错误信息
