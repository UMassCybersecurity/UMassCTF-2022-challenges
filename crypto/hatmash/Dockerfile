FROM ubuntu:20.04

RUN apt-get update && apt-get install -y python3.6 python3-distutils python3-pip python3-apt

RUN useradd -d /home/ctf/ -m -p ctf -s /bin/bash ctf
RUN echo "ctf:ctf" | chpasswd

WORKDIR /home/ctf

COPY hatmash.py .
COPY flag.txt .
COPY ynetd .

RUN chown -R root:root /home/ctf
RUN chmod +x /home/ctf/ynetd

USER ctf
EXPOSE 10001
CMD ./ynetd -p 10001 "python3 hatmash.py"

