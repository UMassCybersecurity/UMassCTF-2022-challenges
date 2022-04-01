FROM ubuntu:20.04

RUN apt-get update && apt-get install -y python3.6 python3-distutils python3-pip python3-apt

RUN useradd -d /home/ctf/ -m -p ctf -s /bin/bash ctf
RUN echo "ctf:ctf" | chpasswd

WORKDIR /home/ctf

COPY fastcrypt_trial.py .
COPY flag.txt .
COPY ynetd .

RUN chown -R root:root /home/ctf
RUN chmod +x /home/ctf/ynetd

USER ctf
EXPOSE 10003
CMD ./ynetd -p 10003 "python3 fastcrypt_trial.py"

