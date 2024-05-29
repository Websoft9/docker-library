echo "Add your CI code here, below is example"

echo "Hello, Apache!" > /usr/local/apache2/htdocs/index.html

### Install packages that you may use for deployment

# apt update -y
# apt install -y wget unzip

### Sample for reference
# rm -rf /usr/local/apache2/htdocs/*
# wget https://websoft9.github.io/docker-library/apps/nginx/demo/demo.zip -P /usr/local/apache2/htdocs
# unzip /usr/local/apache2/htdocs/demo.zip -d /usr/local/apache2/htdocs