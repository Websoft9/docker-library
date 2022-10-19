# image: https://hub.docker.com/r/websoft9dev/discuzq

FROM centos:centos7

LABEL maintainer="help@websoft9.com"
LABEL version="latest"
LABEL description="Ansible"

WORKDIR "/ansible/project"

# Install ansible
RUN yum install -y epel-release 1>/dev/null 2>&1
RUN yum install -y git mosh wget openssl unzip bzip2 expect at tree vim screen pwgen  htop yum-utils gcc jq telnet mlocate
RUN yum install python python3 -y 1>/dev/null 2>&1
RUN yum install ansible -y

RUN python3 -m pip install --upgrade pip && python3 -m pip install -U --force-reinstall requests fabric httplib2 pywinrm

# download template of role, it's to run the tasks of you want to test
RUN git clone https://github.com/Websoft9/role_template

VOLUME "/ansible/project"

# Define the entry point for the docker container.
ENTRYPOINT ["tail", "-f", "/dev/null"]
