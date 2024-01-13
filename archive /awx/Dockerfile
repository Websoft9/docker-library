FROM quay.io/ansible/awx:22.5.0

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
ENV AWX_LOGGING_MODE stdout


USER root
RUN rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial
ADD https://copr.fedorainfracloud.org/coprs/ansible/Rsyslog/repo/epel-9/ansible-Rsyslog-epel-9.repo /etc/yum.repos.d/ansible-Rsyslog-epel-9.repo
# Install runtime requirements
RUN dnf -y update && dnf install -y 'dnf-command(config-manager)' && \
    dnf config-manager --set-enabled crb && \
    dnf -y install acl \
    git-core \
    git-lfs \
    glibc-langpack-en \
    krb5-workstation \
    nginx \
    "openldap >= 2.6.2-3" \
    postgresql \
    rsync \
    rsyslog-8.2102.0-106.el9 \
    subversion \
    sudo \
    vim-minimal \
    which \
    unzip \
    crun \
    gdb \
    gtk3 \
    gettext \
    hostname \
    procps \
    alsa-lib \
    libX11-xcb \
    libXScrnSaver \
    iproute \
    strace \
    vim \
    nmap-ncat \
    libpq-devel \
    nodejs \
    nss \
    make \
    patch \
    socat \
    tmux \
    wget \
    diffutils \
    unzip && \
    dnf -y clean all 
RUN rm -rf /root/.cache && rm -rf /tmp/*
RUN dnf --enablerepo=baseos-debug -y install python3-debuginfo || :
RUN dnf install -y epel-next-release && dnf install -y inotify-tools && dnf remove -y epel-next-release
RUN dnf install -y podman && rpm --restore shadow-utils 2>/dev/null
RUN sed -i -e 's|^#mount_program|mount_program|g' -e '/additionalimage.*/a "/var/lib/shared",' -e 's|^mountopt[[:space:]]*=.*$|mountopt = "nodev,fsync=0"|g' /etc/containers/storage.conf
RUN mkdir -p /etc/containers/registries.conf.d/ && echo "unqualified-search-registries = []" >> /etc/containers/registries.conf.d/force-fully-qualified-images.conf && chmod 644 /etc/containers/registries.conf.d/force-fully-qualified-images.conf
ADD src/config/podman-containers.conf /var/lib/awx/.config/containers/containers.conf
RUN /var/lib/awx/venv/awx/bin/pip install "ansible-core>=2.15.0rc2,<2.16" --no-cache-dir
COPY --from=quay.io/ansible/awx-ee:22.5.0 /usr/bin/receptor /usr/bin/receptor
ENV PATH="/var/lib/awx/venv/awx/bin/:${PATH}"
ENTRYPOINT ["dumb-init", "--"]
