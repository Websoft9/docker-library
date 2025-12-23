# Coze Studio

官方文档：https://www.coze.cn/open/docs/guides

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
2. 修改模型配置相关变量  
  以deepseek为例：
   ```
   MODEL_PROTOCOL_0="ark"
   MODEL_OPENCOZE_ID_0="100001"
   MODEL_NAME_0="deepseek"                      # 模型名称（可自定义）
   MODEL_ID_0="deepseek-reasoner"               # 供应商给出的模型ID
   MODEL_API_KEY_0="sk-xxxxxxxxxxxxxxxxxxxxxxx" # API密钥
   MODEL_BASE_URL_0="https://api.deepseek.com"  # 模型基础url
   ```
   如果需要配置多个模型，可将上述内容复制一份，修改0为其他数字并修改相应的值