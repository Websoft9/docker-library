FROM kasmweb/desktop:1.14.0
USER root

LABEL maintainer="help@websoft9.com"
LABEL version="1.41.0"
LABEL description="Mongo Compass"

ENV HOME /home/kasm-default-profile
ENV STARTUPDIR /dockerstartup
ENV COMPASSVERSION=1.41.0
WORKDIR $HOME


######### Customize Container Here ###########

RUN apt-get update && apt install -y kde-cli-tools  kde-runtime  trash-cli  libglib2.0-bin gvfs-bin gnome-keyring 

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
