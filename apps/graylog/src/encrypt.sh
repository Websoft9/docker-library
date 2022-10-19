#!/bin/bash
export PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin
clear

# Add encrypt script below if use APP_ENCRYPT_PASSWORD at .env file
# ------------- start -------------------------
echo -n $1 | sha256sum | awk '{ print $1 }'
# ------------- end ---------------------------
