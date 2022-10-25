## docker-compose

restart:

| restart参数 |    重启前容器状态 -stop                                     | 重启前容器状态 -start |
| ------ | --------------------------------------------- | ------ |
| no |  stop | stop   |
| on-failure   | stop | stop  |
| unless-stopped   | stop | start  |
| always  | start | start  |
