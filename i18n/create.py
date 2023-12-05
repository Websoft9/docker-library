import glob
import json
from dotenv import dotenv_values

# 读取已有的 translation.json 文件
with open('translation.json', 'r') as f:
    translation = json.load(f)

# 遍历所有 .env 文件
for filename in glob.glob('../apps/*/.env'):
    # 解析 .env 文件
    env_dict = dotenv_values(filename)
    # 遍历所有环境变量
    for key in env_dict.keys():
        # 如果 key 以 'W9_' 开头并以 '_SET' 结尾
        if key.startswith('W9_') and key.endswith('_SET'):
            # 如果 key 不在 translation.json 中，将其添加到 translation.json 中
            if key not in translation:
                translation[key] = ["", ""]

# 将修改后的 translation.json 写回到文件中
with open('translation.json', 'w') as f:
    json.dump(translation, f, indent=4)