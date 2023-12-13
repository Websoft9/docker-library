# image: https://github.com/orgs/ansible-community/packages/container/package/community-ee-base
# docs1: https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-ansible-to-containers
# docs2: https://learn.microsoft.com/en-us/azure/developer/ansible/configure-in-docker-container

FROM ghcr.io/ansible-community/community-ee-base:latest

LABEL maintainer="help@websoft9.com"
LABEL version="latest"
LABEL description="Ansible"

USER root

WORKDIR "/ansible/project"

RUN yum check-update && \
    yum install -y gcc libffi-devel wget openssl vim yum-utils jq unzip curl && \
    yum clean all && \
    ln -s $(command -v pip3) /usr/local/bin/pip && \
    pip3 install --upgrade pip --no-cache-dir && \
    pip3 install --upgrade virtualenv --no-cache-dir && \
    pip3 install jmespath --no-cache-dir && \
    pip3 install requests --no-cache-dir

VOLUME "/ansible/project"

# Define the entry point for the docker container.
# You may want to change this according to your actual needs.
ENTRYPOINT ["tail", "-f", "/dev/null"]