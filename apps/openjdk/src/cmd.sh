echo "Add your CI code here, below is example"

### Install java sample

#cd /usr/src/app
#curl -L -O https://get.jenkins.io/war/latest/jenkins.war
#java -jar jenkins.war --httpPort=8080

### Install maven sample

# curl -o maven.tar.gz https://dlcdn.apache.org/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.tar.gz
# tar -xzf maven.tar.gz --transform 's/^apache-maven-3.9.6/maven/
# echo 'export MAVEN_HOME=/usr/src/app/maven' >> /root/.bashrc
# echo 'export PATH=$PATH:$MAVEN_HOME/bin' >> /root/.bashrc
# source /root/.bashrc

### Install gradle sample

# curl  -L -O  https://services.gradle.org/distributions-snapshots/gradle-8.8-20240412020704+0000-bin.zip
# yum install unzip
# unzip gradle*.zip && rm -rf gradle*.zip
# mv gradle* gradle
# echo 'export GRADLE_HOME=/usr/src/app/gradle' >> /root/.bashrc
# echo 'export PATH=$PATH:$GRADLE_HOME/bin' >> /root/.bashrc
# source /root/.bashrc