#!/bin/bash

env  PYTHON_ROOT_PATH=/data/apps
env  PYTHON_W9_NAME

cd $NODE_ROOT_PATH
pip install django
django-admin startproject mydjango
cd mydjango
python manage.py migrate
echo "ALLOWED_HOSTS = ['*']" >> mydjango/settings.py
python manage.py runserver 0.0.0.0:3000

tail -f /dev/null