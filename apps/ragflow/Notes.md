# RagFlow
## 配置须知
- 默认安装ragflow-cpu版本，默认文档搜索引擎为elasticsearch
- 如需修改为gpu版本/更换搜索引擎，请修改.env文件中的
 ```
 # Application parameters
 DOC_ENGINE=elasticsearch
 DEVICE=cpu
 COMPOSE_PROFILES=${DOC_ENGINE},${DEVICE}
 ```
- 如需启动额外容器，请在这行语句后追加相应容器profiles名，如：（对应名称可在docker-compose.yml文件的相应容器中的profiles参数中找到）
 ```
 COMPOSE_PROFILES=${DOC_ENGINE},${DEVICE},sandbox
 ```
 如果docker-compose.yml文件中相关的容器以及.env文件中相关配置被注释了，需要取消注释

- 详细使用文档请前往官方查询：
  - 中文：https://ragflow.com.cn/docs/dev/
  - English:https://ragflow.io/docs/dev/