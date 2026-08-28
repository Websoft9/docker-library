## docker-compose

restart:

| restart参数 |    重启前容器状态 -stop                                     | 重启前容器状态 -start |
| ------ | --------------------------------------------- | ------ |
| no |  stop | stop   |
| on-failure   | stop | stop  |
| unless-stopped   | stop | start  |
| always  | start | start  |


## Todo

- libs scan should first response the url network reaching

  "help": {
    "db": "MySQL 8.0+ or MariaDB 10.11+"


Install Activepieces on this machine by running `curl -fsSL https://get.activepieces.com | sh` from a folder I choose. It needs Docker Compose v2, so check `docker compose version` first and tell me if it is missing. If port 8080 is already in use, re-run with `--port` and a free port. When it finishes, confirm the stack is healthy with `docker compose -p activepieces ps` and `curl http://localhost:8080/api/v1/health`, then tell me the URL to open and remind me to back up the generated `.env` file.

tests
- change Credential
- root_url?

radom key create