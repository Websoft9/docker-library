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
export DJANGO_SUPERUSER_PASSWORD=$W9_LOGIN_PASSWORD
# 迁移数据库
awx-manage migrate

wait-for-migrations

export PATH=$PATH:/var/lib/awx/venv/awx/bin

awx-manage create_preload_data
awx-manage register_default_execution_environments
# 创建admin账号密码
if output=$(awx-manage createsuperuser --noinput --username=${W9_LOGIN_USER} --email=admin@localhost 2> /dev/null); then
    echo $output
fi
echo "Admin password: ${DJANGO_SUPERUSER_PASSWORD}"

awx-manage create_preload_data
awx-manage register_default_execution_environments

awx-manage provision_instance --hostname="awx_1" --node_type="$MAIN_NODE_TYPE"
awx-manage register_queue --queuename=controlplane --instance_percent=100
awx-manage register_queue --queuename=default --instance_percent=100

if [[ -n "$RUN_MIGRATIONS" ]]; then
    for (( i=1; i<$CONTROL_PLANE_NODE_COUNT; i++ )); do
        for (( j=i + 1; j<=$CONTROL_PLANE_NODE_COUNT; j++ )); do
            awx-manage register_peers "awx_$i" --peers "awx_$j"
        done
    done

    if [[ $EXECUTION_NODE_COUNT > 0 ]]; then
        awx-manage provision_instance --hostname="receptor-hop" --node_type="hop"
        awx-manage register_peers "receptor-hop" --peers "awx_1"
        for (( e=1; e<=$EXECUTION_NODE_COUNT; e++ )); do
            awx-manage provision_instance --hostname="receptor-$e" --node_type="execution"
            awx-manage register_peers "receptor-$e" --peers "receptor-hop"
        done
    fi
fi

exec supervisord -c /etc/supervisord_task.conf