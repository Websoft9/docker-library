
### Default Demo which you can delete it

echo "Add your CI code here, below is example"
echo "Hello, Nginx!" > /usr/share/nginx/html/index.html

### Install packages that you may use for deployment

# apt update -y
# apt install -y wget unzip


### Sample for reference
# rm -rf /usr/share/nginx/html/*
# wget https://websoft9.github.io/docker-library/apps/nginx/demo/demo.zip -P /usr/share/nginx/html
# unzip /usr/share/nginx/html/demo.zip -d /usr/share/nginx/html