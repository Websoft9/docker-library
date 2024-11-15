#!/bin/bash

# Define the ini file
INI_FILE="/usr/local/bin/config.ini"

# Get the packages from the ini file using crudini
packages=$(crudini --get "$INI_FILE" apt packages)

# Convert comma-separated values to space-separated
packages=$(echo "$packages" | tr ',' ' ')

# Install packages one by one
for package in $packages; do
    echo "Start to install $package"
    if apt-get install -y $package; then
        echo "$package installed successfully"
    else
        echo "$package failed to install"
    fi
done