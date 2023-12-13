# image and version from: https://github.com/orgs/ansible-community/packages/container/package/community-ee-base
# docs1: https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-ansible-to-containers
# docs2: https://learn.microsoft.com/en-us/azure/developer/ansible/configure-in-docker-container

FROM ghcr.io/ansible-community/community-ee-base:latest

LABEL maintainer="help@websoft9.com"

# You should change the below if official image latest version changed
LABEL version="2.16.1"
LABEL description="Ansible"

USER root

WORKDIR "/ansible/project"

# Set ansible.cfg
COPY ./test/ansible.cfg /etc/ansible/

# Copy test files
COPY ./test/inventory ./test/
COPY ./test/playbook.yml ./test/

# Install tools
RUN yum check-update; \
    yum install -y wget; \
    yum install -y openssl; \
    yum install -y vim; \
    yum install -y yum-utils; \
    yum install -y jq; \
    yum install -y unzip; \
    yum install -y curl; \
    yum clean all
    
# Install python packages
RUN ln -s $(command -v pip3) /usr/local/bin/pip; \
    pip install --upgrade pip; \
    pip install --upgrade virtualenv; \
    pip install jmspath; \
    pip install requests

VOLUME "/ansible/project"

# Define the entry point for the docker container.
ENTRYPOINT ["tail", "-f", "/dev/null"]