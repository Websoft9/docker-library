#!/bin/bash
sleep 10s

sudo docker cp /data/apps/wordpress/data/backup/wp wordpress:/usr/local/bin
