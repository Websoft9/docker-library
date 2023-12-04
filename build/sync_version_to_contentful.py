import json
import os
from pathlib import Path
from contentful_management import Client
from contentful_management.errors import HTTPError

# 设置 Contentful API 访问参数
ACCESS_TOKEN = os.environ['CONTENTFUL_ACCESS_TOKEN']
SPACE_ID = "ffrhttfighww"

# 初始化 Contentful 管理客户端
client = Client(ACCESS_TOKEN)

def update_contentful(product_name, editions, requirements):
    try:
        # 获取 Contentful 中的 Product entry
        entries = client.entries(SPACE_ID, 'master').all({'content_type': 'product', 'fields.key': product_name})

        # 假设只有一个匹配的 entry
        if entries:
            entry = entries[0]
            # 准备 distribution 更新的数据
            distribution = [{"key": edition['dist'], "value": edition['version']} for edition in editions]
            entry.fields('en-US')['distribution'] = distribution 

            # 准备 requirements 更新的数据
            entry.fields('en-US')['vcpu'] = int(requirements['cpu'])
            entry.fields('en-US')['memory'] = int(requirements['memory'])
            entry.fields('en-US')['storage'] = int(requirements['disk'])

            # 保存和发布更新
            entry.save()
            entry.publish()
            return True
        else:
            print(f"No entry found for product '{product_name}'.")
            return False
    except HTTPError as http_error:
        print(f"Failed to update entry for product '{product_name}'. HTTPError: {http_error}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while updating entry for product '{product_name}': {e}")
        return False

# 初始化计数器
total_updates = 0
successful_updates = 0
failed_updates = 0
failed_products = []

# 遍历 apps 文件夹中的 variables.json 文件
apps_path = Path('apps')
for variables_file in apps_path.rglob('variables.json'):
    try:
        with open(variables_file) as file:
            data = json.load(file)
            product_name = data['name']
            editions = data['edition']
            requirements = data['requirements']
            
            total_updates += 1
            if update_contentful(product_name, editions, requirements):
                successful_updates += 1
            else:
                failed_updates += 1
                failed_products.append(product_name)
    except json.JSONDecodeError as e:
        # 使用父目录的名称来标识出现问题的 JSON 文件
        parent_dir_name = variables_file.parent.name
        print(f"JSON decode error in file {variables_file}: {e}")
        failed_updates += 1
        failed_products.append(parent_dir_name)  # 使用父目录名作为产品名
    except Exception as e:
        # 同样，使用父目录的名称来标识出现问题的 JSON 文件
        parent_dir_name = variables_file.parent.name
        print(f"An unexpected error occurred while processing file {variables_file}: {e}")
        failed_updates += 1
        failed_products.append(parent_dir_name)  # 使用父目录名作为产品名

# 打印更新报告
print(f"Update Summary:\nTotal updates attempted: {total_updates}\nSuccessful updates: {successful_updates}\nFailed updates: {failed_updates}")
if failed_products:
    print(f"Failed product updates: {', '.join(failed_products)}")
