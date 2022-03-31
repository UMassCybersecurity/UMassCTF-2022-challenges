# Stolen from https://github.com/LiveOverflow/pwn_docker_example/blob/master/challenge/Dockerfile

# sudo docker build -t pwn01_baby_overflow_i .
# sudo docker run -d -p 1024:1024 --rm -it pwn01_baby_overflow_i

FROM ubuntu:20.04


RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential

RUN useradd -d /home/ctf/ -m -p ctf -s /bin/bash ctf
RUN echo "ctf:ctf" | chpasswd

WORKDIR /home/ctf

COPY ./app .
COPY ynetd .

RUN chown -R root:root /home/ctf
RUN chmod +x /home/ctf/ynetd

USER ctf
EXPOSE 1229
CMD ./ynetd -p 1229 "python3 jeopardy.py"
