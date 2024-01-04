## Redis

You can set redis by one method of below:

- command: redis-server --requirepass ${REDIS_PASSWORD} --bind 0.0.0.0 --loglevel verbose
- entrypoint: ["redis-server", "/etc/redis.conf"] 