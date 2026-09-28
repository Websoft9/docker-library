#!/bin/bash

GO_ROOT_PATH=/data/apps
GO_W9_NAME=gin

#---------
cd $GO_ROOT_PATH
git clone --depth=1 https://github.com/gin-gonic/examples gin
cd gin/file-binding
go run main.go	
#---------

tail -f /dev/null