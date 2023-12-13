# Test Ansible

1. 运行 Ansible 容器
    ```
    docker run -it -d --name ansible websoft9dev/ansible
    ```

2. 进入容器
   ```
   docker exec -it ansible bash
   ```

3. 使用 vim 编辑 test 目录下的 inventory 文件，修改成您的目标主机
   ```
   vim test/inventory
   ```

4. 运行 Ansible playbook
   ```
   cd test
   ansible-playbook -i inventory playbook.yml
   ```