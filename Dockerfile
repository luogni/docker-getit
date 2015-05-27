FROM ubuntu:14.04
MAINTAINER Luca Ognibene, luca.ognibene@gmail.com

RUN apt-get update && \
    apt-get upgrade -y

RUN apt-get update && apt-get -y install \
    python-lxml \
    python-requests \
    python-cssselect

RUN adduser --disabled-login --gecos '' getit
COPY "parsesite.py" "/home/getit/"
COPY "getit.py" "/home/getit/"
COPY "getcmds.py" "/home/getit/"
RUN chmod a+x /home/getit/*.py

USER getit
WORKDIR /home/getit

VOLUME ["/media"]

ENTRYPOINT ["/home/getit/getit.py"]
