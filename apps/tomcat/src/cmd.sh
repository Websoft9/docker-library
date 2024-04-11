###  This script is running before tomcat starting  ##############
###  You can add your CI code here, below is example

cp -r webapps.dist/* webapps


### Install os packages
# apt update -y && apt install unzip -y


### Install java sample, access by: http://URL/sample
# cd /usr/local/tomcat/webapps
# wget https://tomcat.apache.org/tomcat-10.0-doc/appdev/sample/sample.war