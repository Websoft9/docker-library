# update time: 20231226

FROM kasmweb/desktop:1.14.0
USER root

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="Mongo Compass packaged by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/mongocompass" \
      org.opencontainers.image.title="OpenCart" \
      org.opencontainers.image.vendor="Websoft9 Inc." \
      org.opencontainers.image.version="1.41.0"

ENV HOME /home/kasm-default-profile
ENV STARTUPDIR /dockerstartup
ENV COMPASSVERSION=1.41.0
WORKDIR $HOME


######### Customize Container Here ###########

RUN apt update -y && \
    apt install -y kde-cli-tools && \
    apt install -y kde-runtime && \
    apt install -y trash-cli && \
    apt install -y libglib2.0-bin && \
    apt install -y gvfs-bin && \
    apt install -y gnome-keyring 

RUN apt install -y sudo \
    && useradd -m -d /home/kasm-user -s /bin/bash kasm-user \
    && echo 'kasm-user ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

RUN wget https://downloads.mongodb.com/compass/mongodb-compass_$COMPASSVERSION_amd64.deb \
    && dpkg -i mongodb-compass_$COMPASSVERSION_amd64.deb \
    && cp /usr/share/applications/mongodb-compass.desktop $HOME/Desktop/ \
    && chmod +x $HOME/Desktop/mongodb-compass.desktop \
    && chown 1000:1000 $HOME/Desktop/mongodb-compass.desktop

RUN desktop-file-edit \
--set-key="Exec" --set-value="sudo mongodb-compass %U --no-sandbox" \
$HOME/Desktop/mongodb-compass.desktop

RUN  rm -rf mongodb-compass_$COMPASSVERSION_amd64.deb

######### End Customizations ###########

RUN chown 1000:0 $HOME
RUN $STARTUPDIR/set_user_permission.sh $HOME

ENV HOME /home/kasm-user
WORKDIR $HOME
RUN mkdir -p $HOME && chown -R 1000:0 $HOME

USER 1000
