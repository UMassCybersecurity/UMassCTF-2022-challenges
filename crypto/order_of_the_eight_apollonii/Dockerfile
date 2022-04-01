FROM ubuntu:20.04

RUN apt-get update
RUN apt-get -y install python3-pip

RUN pip install --no-cache-dir numpy


RUN useradd -d /home/ctf/ -m -p ctf -s /bin/bash ctf
RUN echo "ctf:ctf" | chpasswd

WORKDIR /home/ctf

COPY ordereightapollonii.py .
COPY flag.txt .
COPY ynetd .

RUN chown -R root:root /home/ctf
RUN chmod +x /home/ctf/ynetd

USER ctf
EXPOSE 10002
CMD ./ynetd -p 10002 "python3 ordereightapollonii.py"

