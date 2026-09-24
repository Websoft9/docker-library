#!/bin/bash

cp /opt/config/php/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
chmod +x /etc/supervisor/conf.d/supervisord.conf

# start by supervisord
/usr/bin/supervisord
supervisorctl start $PHP_APP
tail -f /dev/null
