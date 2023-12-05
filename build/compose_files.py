import sys
import os
import subprocess

# sys.argv[1] is the first argument passed to the script
input_arg = sys.argv[1]

# Split the input argument on commas to get a list of filenames
filenames = input_arg.split(',')

# Remove any empty strings from the list
filenames = [filename for filename in filenames if filename]


for filename in filenames:
    # 获取文件的目录和基础名
    directory, basename = os.path.split(filename)

    # 从基础名中提取 * 部分
    name_part = basename.split('-')[2].split('.')[0]  # 从 'docker-compose-*.yml' 中提取 '*'

    # 构造新的文件名
    new_filename = os.path.join(directory, f'docker-compose-{name_part}-merged.yml')

    # 构造 docker-compose 命令
    cmd = ['docker-compose', '-f', 'docker-compose.yml', '-f', filename, 'config', '>', new_filename]

    # 执行命令
    subprocess.run(' '.join(cmd), shell=True, check=True)
