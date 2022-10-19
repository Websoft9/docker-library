#! /bin/bash
echo root:$WEBMIN_PASSWORD | chpasswd
sed -i 's;ssl=1;ssl=0;' /etc/webmin/miniserv.conf && systemctl enable cron && service webmin start && tail -f /dev/null
