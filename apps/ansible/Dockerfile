# refer to: 
# refer to: https://learn.microsoft.com/en-us/azure/developer/ansible/configure-in-docker-container

FROM ghcr.io/ansible-community/community-ee-base:latest

LABEL maintainer="help@websoft9.com"
LABEL version="latest"
LABEL description="Ansible"

WORKDIR "/ansible/project"

RUN yum check-update; \
    yum install -y gcc libffi-devel python3 epel-release; \
    yum install -y python3-pip; \
    yum install -y wget; \
    yum install -y openssl; \
    yum install -y vim; \
    yum install -y yum-utils \
    yum install -y jq \
    yum install -y unzip \
    yum install -y curl \
    yum clean all

RUN pip3 install --upgrade pip; \
    pip3 install --upgrade virtualenv; \
    pip3 install pywinrm[kerberos]; \
    pip3 install pywinrm; \
    pip3 install jmspath; \
    pip3 install requests; \
    
# download template of role, it's to run the tasks of you want to test -- need transfer
# RUN git clone https://github.com/Websoft9/role_template

VOLUME "/ansible/project"

# Define the entry point for the docker container.
ENTRYPOINT ["tail", "-f", "/dev/null"]