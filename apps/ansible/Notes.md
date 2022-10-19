# Ansible

采用 CentOS7 作为基础镜像，更好的解决用户使用 Ansible 时面临的灵活可控问题

## 体验改善

1. 在宿主机上增加更多的 alias
```
alias ansible='docker exec -it ansible ansible'
alias ansible-playbook='docker exec -it ansible ansible-playbook'
```

2. 内置role_template (已完成)