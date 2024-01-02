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

ENV HOME /home/kasm-default-profile
ENV STARTUPDIR /dockerstartup
ENV COMPASSVERSION=1.41.0
WORKDIR $HOME


######### Customize Container Here ###########

# 设置环境变量，防止在docker构建时出现交互式提示
ENV DEBIAN_FRONTEND noninteractive

# 更新软件包列表
RUN apt-get update

# 安装MongoDB Compass依赖
RUN apt-get install -y wget gnupg

# 添加MongoDB的公钥
RUN wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | apt-key add -

# 添加MongoDB的repository
RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-5.0.list

# 再次更新软件包列表
RUN apt-get update

# 安装MongoDB Compass
RUN apt-get install -y mongodb-compass

# 清理不再需要的文件
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# RUN apt update -y && \
#     apt install -y kde-cli-tools && \
#     apt install -y kde-runtime && \
#     apt install -y trash-cli && \
#     apt install -y libglib2.0-bin && \
#     apt install -y gvfs-bin && \
#     apt install -y gnome-keyring 

# RUN apt install -y sudo \
#     && useradd -m -d /home/kasm-user -s /bin/bash kasm-user \
#     && echo 'kasm-user ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

# RUN wget https://downloads.mongodb.com/compass/mongodb-compass_$COMPASSVERSION_amd64.deb \
#     && dpkg -i mongodb-compass_$COMPASSVERSION_amd64.deb
    
# RUN cp /usr/share/applications/mongodb-compass.desktop $HOME/Desktop/ \
#     && chmod +x $HOME/Desktop/mongodb-compass.desktop \
#     && chown 1000:1000 $HOME/Desktop/mongodb-compass.desktop

# RUN desktop-file-edit \
#     --set-key="Exec" --set-value="sudo mongodb-compass %U --no-sandbox" \
#     $HOME/Desktop/mongodb-compass.desktop

# RUN  rm -rf mongodb-compass_$COMPASSVERSION_amd64.deb

######### End Customizations ###########

RUN chown 1000:0 $HOME
RUN $STARTUPDIR/set_user_permission.sh $HOME

ENV HOME /home/kasm-user
WORKDIR $HOME
RUN mkdir -p $HOME && chown -R 1000:0 $HOME

USER 1000