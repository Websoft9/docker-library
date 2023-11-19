import json
import os

# 从文件中读取单词
with open('itemname_fields', 'r', encoding='utf-8') as f:
    words = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# 列出你的目标语言
languages = ["zh", "fr", "de", "ja", "en"]

# 对每种语言生成一个翻译文件
for lang in languages:
    filename = f'translation_{lang}.json'
    
    if os.path.exists(filename):
        # 如果文件已经存在，加载已有的翻译
        with open(filename, 'r', encoding='utf-8') as f:
            translation = json.load(f)
    else:
        # 如果文件不存在，创建一个新的翻译
        translation = {}
    
    # 对每个单词，如果它还没有翻译，添加一个空的翻译
    for word in words:
        if word not in translation:
            translation[word] = ""

    # 保存翻译文件
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(translation, f, ensure_ascii=False, indent=4)
