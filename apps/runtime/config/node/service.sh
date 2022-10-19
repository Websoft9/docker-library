#!/bin/bash

installApp(){
   
mkdir -p $1/$2  && cd $1/$2
echo `pwd`
yarn add express
cat > $1/$2/main.js <<-EOF
const express = require("express");
const app = express();
const hostname = "0.0.0.0";
const port = 3000;
app.get("/", (req, res) => {
       res.send("Hello World");
});
app.listen(port, () => {
       console.log(`Server running at http://${hostname}:${port}/`);
});
EOF
}

# install pm2 and setup runtime project
echo "Create sample and pm2 for your reference"
yarn global add pm2
installApp $NODE_ROOT_PATH $NODE_APP_NAME

if [ "$NODE_APP_NAME"  == "express" ];then
  cd $NODE_ROOT_PATH
  pm2 $NODE_APP_NAME/main.js
elif [ "$NODE_APP_NAME" == "appname" ];then
  echo "start appname"
else
  echo "Not support APP:$NODE_APP_NAME now!"
fi

tail -f /dev/null
