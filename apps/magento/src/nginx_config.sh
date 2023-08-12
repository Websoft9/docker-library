#!/bin/bash
        
sudo sed -i "s/proxy_buffer_size          4k/proxy_buffer_size          128k/g" /etc/nginx/conf.d/default.conf
sudo sed -i "s/proxy_buffers              4 32k/proxy_buffers              4 256k/g" /etc/nginx/conf.d/default.conf
sudo sed -i "s/proxy_busy_buffers_size    64k/proxy_busy_buffers_size    256k/g" /etc/nginx/conf.d/default.conf
sudo sed -i "s/proxy_temp_file_write_size 64k/proxy_temp_file_write_size 256k/g" /etc/nginx/conf.d/default.conf
sudo sed -i '/proxy_temp_file_write_size/a \ \ \ \ \ \ \ \ fastcgi_buffers 16 16k;\n\ \ \ \ \ \ \ \ fastcgi_buffer_size 32k;'  /etc/nginx/conf.d/default.conf