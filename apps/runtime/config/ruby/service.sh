#!/bin/bash

RUBY_ROOT_PATH=/data/apps
RUBY_APP_NAME=rails

installRails(){

gem install rails
rails --version
rails new myrails
cd myrails
}

cd $RUBY_ROOT_PATH  && installRails

cd $RUBY_ROOT_PATH/myrails && bin/rails server -b 0.0.0.0 -p 3000

tail -f /dev/null