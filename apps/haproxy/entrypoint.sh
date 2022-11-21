# replace password
sudo sed -i "s/admin:.*/admin:$APP_PASSWORD/g" /data/apps/haproxy/src/haproxy.cfg

# up the native entrypoint.sh and cmd
exec "$@"
/docker-entrypoint.sh haproxy -f /usr/local/etc/haproxy/haproxy.cfg