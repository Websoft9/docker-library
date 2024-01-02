# update time: 20231226
# kasmweb refer to: https://www.kasmweb.com/docs/latest/how_to/building_images.html
# kasmweb images: https://github.com/kasmtech/workspaces-images/tree/develop
# compass refer to: https://www.mongodb.com/docs/compass/current/install/

FROM kasmweb/desktop:1.14.0
USER root

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="Mongo Compass packaged by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/mongocompass" \
      org.opencontainers.image.title="Mongo Compass" \
      org.opencontainers.image.vendor="Websoft9 Inc." \
      org.opencontainers.image.version="1.41.0"

ENV COMPASSVERSION=1.41.0
ENV STARTUPDIR /dockerstartup
ENV HOME /home/kasm-user
WORKDIR $HOME

# Install MongoDB Compass
RUN apt update -y && apt install -y \
    sudo \
    --no-install-recommends && \
    useradd -m -d $HOME -s /bin/bash kasm-user && \
    echo 'kasm-user ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers && \
    wget -q https://downloads.mongodb.com/compass/mongodb-compass_${COMPASSVERSION}_amd64.deb && \
    dpkg -i mongodb-compass_${COMPASSVERSION}_amd64.deb && \
    rm -rf mongodb-compass_${COMPASSVERSION}_amd64.deb /var/lib/apt/lists/* && \
    cp /usr/share/applications/mongodb-compass.desktop $HOME/Desktop/ && \
    chmod +x $HOME/Desktop/mongodb-compass.desktop && \
    chown 1000:1000 $HOME/Desktop/mongodb-compass.desktop && \
    desktop-file-edit --set-key="Exec" --set-value="sudo mongodb-compass %U --no-sandbox" $HOME/Desktop/mongodb-compass.desktop

# Set permissions
RUN chown 1000:0 $HOME && \
    $STARTUPDIR/set_user_permission.sh $HOME && \
    mkdir -p $HOME && \
    chown -R 1000:0 $HOME

USER 1000