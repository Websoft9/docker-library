#!/usr/bin/env bash
if [ `id -u` -ge 500 ]; then
    echo "awx:x:`id -u`:`id -g`:,,,:/var/lib/awx:/bin/bash" >> /tmp/passwd
    cat /tmp/passwd > /etc/passwd
    rm /tmp/passwd
fi

if [ -n "${AWX_KUBE_DEVEL}" ]; then
    pushd /awx_devel
    make awx-link
    popd

    export SDB_NOTIFY_HOST=$MY_POD_IP
fi

set -e

wait-for-migrations

export PATH=$PATH:/var/lib/awx/venv/awx/bin

# 迁移数据库
awx-manage migrate

awx-manage create_preload_data
awx-manage register_default_execution_environments
# 创建admin账号密码
if output=$(awx-manage createsuperuser --noinput --username=admin --email=admin@localhost 2> /dev/null); then
    echo $output
fi
echo "Admin password: ${DJANGO_SUPERUSER_PASSWORD}"

awx-manage provision_instance
awx-manage register_queue --queuename=controlplane --instance_percent=100
awx-manage register_queue --queuename=default --instance_percent=100

awx-manage provision_instance --hostname="receptor-hop" --node_type="hop"
awx-manage register_peers "receptor-hop" --peers "awx_ee"
awx-manage provision_instance --hostname="receptor-1" --node_type="execution"
awx-manage register_peers "receptor-1" --peers "receptor-hop"

exec supervisord -c /etc/supervisord_task.conf