echo -n '$1' | sha256sum | awk '{ print $1 }'
