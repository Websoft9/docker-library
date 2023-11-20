#!/bin/bash

# Initialize an empty JSON object
json='{"apps": {}}'

for dir in $(find ./apps -maxdepth 1 -mindepth 1 -type d)
do
    dirname="$(basename "$dir")"

    if [ -f "$dir/variables.json" ]; then
        release=$(jq -r '.release' "$dir/variables.json")

        if [ "$release" = "true" ]; then
            # Check if .env file exists in the directory
            if [ -f "$dir/.env" ]; then
                # Look for lines containing "_SET=" and print them
                grep "_SET=" "$dir/.env" | while read -r line ; do
                    echo "$dirname: is need convert"
                    # Split the line on "=" and print the key and value
                    key=$(echo $line | cut -d '=' -f 1)
                    value=$(echo $line | cut -d '=' -f 2-)
                    echo "Key: $key"
                    echo "Value: $value"

                    # Add the key-value pair to the JSON object
                    
                done
            else
                echo "$dirname: .env not found"
            fi
        fi
    else
        echo "$dirname: variables.json not found"
    fi
done

# Print the final JSON object
echo $json | jq .
