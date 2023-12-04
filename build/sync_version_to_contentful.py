import json
import os
from pathlib import Path
from contentful_management import Client

# 设置 Contentful API 访问参数
ACCESS_TOKEN = os.environ['CONTENTFUL_ACCESS_TOKEN']
SPACE_ID = "ffrhttfighww"

# 初始化 Contentful 管理客户端
client = Client(ACCESS_TOKEN)

def update_contentful(product_name, editions, requirements):
    # 获取 Contentful 中的 Product entry
    entries = client.entries(SPACE_ID, 'master').all({'content_type': 'product', 'fields.key': product_name})

    # 假设只有一个匹配的 entry
    if entries:
        entry = entries[0]
        # 准备 distribution 更新的数据
        distribution = [{"key": edition['dist'], "value": edition['version']} for edition in editions]
        entry.fields('en-US')['distribution'] = distribution 

        # 准备 requirements 更新的数据
        entry.fields('en-US')['vcpu'] = requirements['cpu']
        entry.fields('en-US')['memory'] = requirements['memory']
        entry.fields('en-US')['storage'] = requirements['disk']

        # 保存和发布更新
        entry.save()
        entry.publish()

# 遍历 apps 文件夹中的 variables.json 文件
# apps_path = Path('apps')
# for variables_file in apps_path.rglob('variables.json'):
#     with open(variables_file) as file:
#         data = json.load(file)
#         product_name = data['name']
#         editions = data['edition']
#         requirements = data['requirements']
#         update_contentful(product_name, editions, requirements)

update_contentful("wordpress", [{"dist": "wordpress", "version": "5.7.2"}], {"cpu": "1", "memory": "1", "disk": "10"})
