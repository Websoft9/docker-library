#!/bin/bash

if [ -f "/usr/local/bin/cmd.sh" ]; then
    chmod +x /usr/local/bin/cmd.sh
    bash /usr/local/bin/cmd.sh
else
    echo "/usr/local/bin/cmd.sh does not exist."
fi

supervisord
supervisorctl start apache
supervisorctl start phpfpm
tail -n 1000 -f /var/log/supervisord.log