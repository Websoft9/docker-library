import json
import argparse

# 设置命令行参数
parser = argparse.ArgumentParser(description='Update JS translation files from a JSON file.')
parser.add_argument('json_file', help='The path to the translation.json file')
parser.add_argument('en_js_file', help='The path to the po.en_US.js file')
parser.add_argument('zh_js_file', help='The path to the po.zh_CN.js file')

# 解析命令行参数
args = parser.parse_args()

# 读取translation.json文件
with open(args.json_file, "r") as f:
    translation = json.load(f)

# 读取po.en_US.js文件
with open(args.en_js_file, "r") as f:
    en_lines = f.readlines()

# 读取po.zh_CN.js文件
with open(args.zh_js_file, "r") as f:
    zh_lines = f.readlines()

# 定义一个函数，用于在js文件中查找或替换key和value
def update_js(lines, key, value):
    # 遍历每一行
    for i, line in enumerate(lines):
        # 如果找到了key
        if f'"{key}": [' in line:
            # 替换value, 确保不在最后一行添加逗号
            lines[i+1] = f"        null,\n"
            lines[i+2] = f"        \"{value}\"\n"
            # 检查下一行是否是数组结束，如果不是则添加逗号
            if not lines[i+3].strip().startswith(']'):
                lines[i+2] = lines[i+2].rstrip() + ",\n"
            # 返回True表示已经更新
            return True
    # 如果没有找到key，就在最后一行前插入新的key和value
    # 确保在倒数第二行添加逗号
    if not lines[-2].strip().endswith(','):
        lines[-2] = lines[-2].rstrip() + ",\n"
    lines.insert(-1, f"    \"{key}\": [\n")
    lines.insert(-1, f"        null,\n")
    lines.insert(-1, f"        \"{value}\"\n")
    lines.insert(-1, f"    ]\n")
    # 返回False表示已经插入
    return False

# 遍历translation.json的每一个键值对
for key, values in translation.items():
    # 获取英文和中文的value
    en_value = values[0]
    zh_value = values[1]
    # 在po.en_US.js文件中更新或插入key和value
    update_js(en_lines, key, en_value)
    # 在po.zh_CN.js文件中更新或插入key和value
    update_js(zh_lines, key, zh_value)

# 写入po.en_US.js文件
with open(args.en_js_file, "w") as f:
    f.writelines(en_lines)

# 写入po.zh_CN.js文件
with open(args.zh_js_file, "w") as f:
    f.writelines(zh_lines)

# 打印完成信息
print("同步完成！")
