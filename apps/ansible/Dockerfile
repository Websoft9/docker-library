# refer to: 
# refer to: https://learn.microsoft.com/en-us/azure/developer/ansible/configure-in-docker-container

FROM ghcr.io/ansible-community/community-ee-base:latest

LABEL maintainer="help@websoft9.com"
LABEL version="latest"
LABEL description="Ansible"

ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

WORKDIR "/ansible/project"

# Install ansible
RUN yum install -y epel-release 1>/dev/null 2>&1
RUN yum install -y git mosh gcc wget libffi-devel openssl unzip bzip2 expect at tree vim screen pwgen  htop yum-utils gcc jq telnet mlocate epel-release
RUN yum install python python3 -y 1>/dev/null 2>&1
RUN yum clean all

# Install python module
RUN python3 -m pip install --upgrade pip virtualenv && python3 -m pip install -U --force-reinstall requests fabric httplib2 pywinrm[kerberos] pywinrm jmspath

# download template of role, it's to run the tasks of you want to test -- need transfer
# RUN git clone https://github.com/Websoft9/role_template

VOLUME "/ansible/project"

# Define the entry point for the docker container.
ENTRYPOINT ["tail", "-f", "/dev/null"]