#!/bin/sh
set -eu

# The Web Console IP allow-list only permits loopback, so external access
# returns 403 through the published port. Layout differs by version:
#   - 5.19.x, 6.2.x: single Spring XML at conf/jetty.xml
#     (inetAccessIncludeLoopbackV4/V6 beans with <list><value> entries)
#   - 6.3.x: modular conf/jetty/jetty-security.xml (<Item> array)
# Append all-IPv4/IPv6 CIDRs to the existing allow-list entries,
# idempotently, then hand control to the official entrypoint.

# --- 5.19.x / 6.2.x: extend the loopback include lists ------------------
JETTY_XML="/opt/apache-activemq/conf/jetty.xml"
if [ -f "$JETTY_XML" ] && ! grep -q '0.0.0.0/0' "$JETTY_XML"; then
  sed -i 's|<list><value>127.0.0.1</value></list>|<list><value>127.0.0.1</value><value>0.0.0.0/0</value></list>|' "$JETTY_XML"
  sed -i 's|<list><value>::1</value></list>|<list><value>::1</value><value>::/0</value></list>|' "$JETTY_XML"
fi

# 5.19.x only: the console CSP header contains "upgrade-insecure-requests",
# which makes browsers force every http resource to https on a plain-http
# console, breaking the page. Drop that directive. 6.2/6.3 do not ship it.
if [ -f "$JETTY_XML" ] && grep -q 'upgrade-insecure-requests' "$JETTY_XML"; then
  sed -i 's/upgrade-insecure-requests; //g' "$JETTY_XML"
fi

# --- 6.3.x: append items after the IPv6 loopback -------------------------
JETTY_SECURITY_XML="/opt/apache-activemq/conf/jetty/jetty-security.xml"
if [ -f "$JETTY_SECURITY_XML" ] && ! grep -q '0.0.0.0/0' "$JETTY_SECURITY_XML"; then
  sed -i '/<Item>::1<\/Item>/a\              <Item>0.0.0.0\/0<\/Item>\
              <Item>::\/0<\/Item>' "$JETTY_SECURITY_XML"
fi

# 5.19.x quirk: the official entrypoint writes ACTIVEMQ_WEB_USER/PASSWORD
# into users.properties, but the 5.19 Web Console authenticates against
# jetty-realm.properties (default "admin: admin"). Sync the same password.
JETTY_REALM="/opt/apache-activemq/conf/jetty-realm.properties"
if [ -f "$JETTY_REALM" ] && [ -n "${ACTIVEMQ_WEB_USER:-}" ]; then
  PASSWORD="${ACTIVEMQ_WEB_PASSWORD:-admin}"
  sed -i "s/^admin:.*/admin: ${PASSWORD}, admin/" "$JETTY_REALM"
fi

# The official entrypoint expects the broker command as "$@" (image CMD is
# "activemq console"). Some deployers override the image CMD, so default it
# here when nothing was passed.
if [ "$#" -eq 0 ]; then
  set -- activemq console
fi

exec /usr/local/bin/entrypoint.sh "$@"
