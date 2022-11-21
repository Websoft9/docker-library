# replace password at /usr/local/etc/haproxy/haproxy.cfg, to do
# target line: stats auth admin:uQ8E1wVTzG8SOk3!

# up the native entrypoint.sh and cmd
exec "$@"

/usr/local/bin/docker-entrypoint.sh haproxy -f /usr/local/etc/haproxy/haproxy.cfg