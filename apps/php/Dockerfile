# 使用 ARG 来读取环境变量
ARG PHP_VERSION=${W9_VERSION}

FROM php:${PHP_VERSION}

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="PHP runtime by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/php" \
      org.opencontainers.image.title="php" \
      org.opencontainers.image.vendor="Websoft9 Inc." \
      org.opencontainers.image.version="${PHP_VERSION}"

# 设置环境变量以避免交互式配置
ENV DEBIAN_FRONTEND=noninteractive

# 安装必要的工具，包括 crudini 和 bash
RUN apt-get update && \
    apt-get install -y \
    crudini \
    bash \
    && apt-get clean

# 复制脚本和配置文件到容器中
COPY src/extensions.ini /usr/local/bin/extensions.ini
COPY src/apt_install.sh /usr/local/bin/apt_install.sh
COPY src/apt_install.sh /usr/local/bin/php_install.sh

# 给予脚本执行权限
RUN chmod +x /usr/local/bin/apt_install.sh
RUN chmod +x /usr/local/bin/php_install.sh

# 运行脚本
RUN /usr/local/bin/apt_install.sh
RUN /usr/local/bin/php_install.sh