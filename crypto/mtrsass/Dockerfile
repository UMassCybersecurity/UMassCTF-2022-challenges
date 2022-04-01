FROM ubuntu:20.04

RUN apt-get update
RUN apt-get -y install python3-pip

RUN pip install --no-cache-dir pycryptodome 

RUN useradd -d /home/ctf/ -m -p ctf -s /bin/bash ctf
RUN echo "ctf:ctf" | chpasswd

WORKDIR /home/ctf

COPY mtrsass.py .
COPY flag.txt .
COPY ynetd .

RUN chown -R root:root /home/ctf
RUN chmod +x /home/ctf/ynetd

USER ctf
EXPOSE 10000
CMD ./ynetd -p 10000 "python3 mtrsass.py"

