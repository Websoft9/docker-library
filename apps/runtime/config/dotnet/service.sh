#!/bin/bash

DOTNET_ROOT_PATH=/data/apps
DOTNET_APP_NAME=aspnet

apt update
apt install unzip

installSample(){
cd $DOTNET_ROOT_PATH
git clone --depth=1 https://github.com/dotnet/dotnet-docker
cp -r dotnet-docker/samples/aspnetapp  ./myapp
rm -rf dotnet-docker
cd myapp/aspnetapp
dotnet run --urls=http://0.0.0.0:8080
}

installSample
tail -f /dev/null