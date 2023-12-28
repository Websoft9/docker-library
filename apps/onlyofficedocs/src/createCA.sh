mkdir /var/www/onlyoffice/Data/certs
cd /var/www/onlyoffice/Data/certs
openssl genrsa -out onlyoffice.key 2048
openssl req -new -newkey rsa:2048 -nodes -keyout onlyoffice.key -out onlyoffice.csr -subj "/C=US/ST=California/L=San Francisco/O=My Company Name/OU=IT Department/CN=www.example.com/emailAddress=admin@example.com"
openssl x509 -req -days 365 -in onlyoffice.csr -signkey onlyoffice.key -out onlyoffice.crt
openssl dhparam -out dhparam.pem 2048
