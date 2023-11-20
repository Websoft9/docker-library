sed -i "s/password=\"biadmin\"/password=\"$W9_PASSWORD\"/g" /home/knowage/apache-tomcat/webapps/knowage/WEB-INF/conf/config/internal_profiling.xml
sed -i "s/password=\"biadmin\"/password=\"$W9_PASSWORD\"/g" /home/knowage/apache-tomcat/webapps/knowage/WEB-INF/conf/webapp/authorizations.xml
mysqladmin -uroot -p$DB_PASS -h 127.0.0.1 knowage -e "DELETE FROM knowage.SBI_USER;"

./entrypoint.sh ./apache-tomcat/bin/startup.sh
