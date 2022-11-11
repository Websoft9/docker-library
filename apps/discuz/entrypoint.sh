#!/bin/bash
# refer to:This shell scritp is based on https://github.com/joomla-docker/docker-joomla/blob/master/4.1/php7.4/apache/docker-entrypoint.sh

set -e

if [[ "$1" == apache2* ]] || [ "$1" == php-fpm ]; then
        uid="$(id -u)"
        gid="$(id -g)"
        if [ "$uid" = '0' ]; then
                case "$1" in
                apache2*)
                        user="${APACHE_RUN_USER:-www-data}"
                        group="${APACHE_RUN_GROUP:-www-data}"

                        # strip off any '#' symbol ('#1000' is valid syntax for Apache)
                        pound='#'
                        user="${user#$pound}"
                        group="${group#$pound}"

                        # set user if not exist
                        if ! id "$user" &>/dev/null; then
                                # get the user name
                                : "${USER_NAME:=www-data}"
                                # change the user name
                                [[ "$USER_NAME" != "www-data" ]] &&
                                        usermod -l "$USER_NAME" www-data &&
                                        groupmod -n "$USER_NAME" www-data
                                # update the user ID
                                groupmod -o -g "$user" "$USER_NAME"
                                # update the user-group ID
                                usermod -o -u "$group" "$USER_NAME"
                        fi
                        ;;
                *) # php-fpm
                        user='www-data'
                        group='www-data'
                        ;;
                esac
        else
                user="$uid"
                group="$gid"
        fi

        if [ ! -e index.php ] && [ ! -e source/module/portal/portal_view.php ]; then
                # if the directory exists and Discuz doesn't appear to be installed AND the permissions of it are root:root, let's chown it (likely a Docker-created directory)
                if [ "$uid" = '0' ] && [ "$(stat -c '%u:%g' .)" = '0:0' ]; then
                        chown "$user:$group" .
                fi

                echo >&2 "Discuz not found in $PWD - copying now..."
                if [ "$(ls -A)" ]; then
                        echo >&2 "WARNING: $PWD is not empty - press Ctrl+C now if this is an error!"
                        (
                                set -x
                                ls -A
                                sleep 10
                        )
                fi
                # use full commands
                # for clearer intent
                sourceTarArgs=(
                        --create
                        --file -
                        --directory /usr/src/discuz/upload
                        --one-file-system
                        --owner "$user" --group "$group"
                )
                targetTarArgs=(
                        --extract
                        --file -
                )
                if [ "$uid" != '0' ]; then
                        # avoid "tar: .: Cannot utime: Operation not permitted" and "tar: .: Cannot change mode to rwxr-xr-x: Operation not permitted"
                        targetTarArgs+=(--no-overwrite-dir)
                fi

                tar "${sourceTarArgs[@]}" . | tar "${targetTarArgs[@]}"

                echo >&2 "Complete! Discuz has been successfully copied to $PWD"
        fi

fi

exec "$@"
