echo "Add your CI code here, below is example"

#cd /usr/src/app
#curl -L -O https://get.jenkins.io/war/latest/jenkins.war
#java -jar jenkins.war --httpPort=8080

## install maven3.9.6:https://maven.apache.org/install.html
# curl -o maven.tar.gz https://dlcdn.apache.org/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.tar.gz
# tar xzvf maven.tar.gz
# echo 'export MAVEN_HOME=/usr/src/app/apache-maven-3.9.6' >> /root/.bashrc
# echo 'export PATH=$PATH:$MAVEN_HOME/bin' >> /root/.bashrc
# source /root/.bashrc

## install gradle8.8:https://docs.gradle.org/current/userguide/installation.html#ex-installing-manually
# curl  -L -O  https://services.gradle.org/distributions-snapshots/gradle-8.8-20240412020704+0000-bin.zip
# yum install unzip
# unzip gradle-8.8-20240412020704+0000-bin.zip
# mv gradle-8.8-20240412020704+0000 gradle-8.8
# echo 'export GRADLE_HOME=/usr/src/app/gradle-8.8' >> /root/.bashrc
# echo 'export PATH=$PATH:$GRADLE_HOME/bin' >> /root/.bashrc
