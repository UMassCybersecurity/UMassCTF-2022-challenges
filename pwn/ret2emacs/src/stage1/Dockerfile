FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
  build-essential \
  && rm -rf /var/lib/apt/lists/*
WORKDIR /tmp/
COPY ynetd.c ./
COPY Makefile ./
RUN make

FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
  docker.io \
  && rm -rf /var/lib/apt/lists/*
WORKDIR /root/
COPY --from=0 /tmp/ynetd /root/ynetd
COPY ./spawn-emacs.sh /root/
RUN chmod +x /root/spawn-emacs.sh
CMD [ "./ynetd", "-p", "6522", "./spawn-emacs.sh" ]
