## Tomcat

### 运行 war 包

进入 **tomcat** 容器，下载官方示例，会自动解压

```
cd /usr/local/tomcat/webapps && wget https://tomcat.apache.org/tomcat-10.0-doc/appdev/sample/sample.war

cd /usr/local/tomcat/webapps && wget https://tomcat.apache.org/tomcat-10.0-doc/appdev/sample/sample.war -O ROOT.war

```

ROOT.war 会自动解压到根目录，而不包含路径