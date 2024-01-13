#!/bin/bash
# customrized cmd powered by Websoft9

if [[ -f /www/server/panel/data/admin_path.pl ]]; then
    rm -f /www/server/panel/data/admin_path.pl 
    echo $BAOTA_USER | bt 6  
    echo $BAOTA_PASSWORD | bt 5 
else
    echo "Initialization has been completed before this time!"
fi
/aapanel.sh || /bt.sh
