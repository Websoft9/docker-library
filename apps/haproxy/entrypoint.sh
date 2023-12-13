# replace password at /usr/local/etc/haproxy/haproxy.cfg, to do
# target line: stats auth admin:uQ8E1wVTzG8SOk3!

# up the native entrypoint.sh and cmd
exec "$@"
echo "$(sed "s/admin:.*/admin:$W9_LOGIN_PASSWORD/g" /usr/local/etc/haproxy/haproxy.cfg)" > /usr/local/etc/haproxy/haproxy.cfg
/usr/local/bin/docker-entrypoint.sh haproxy -f /usr/local/etc/haproxy/haproxy.cfg
