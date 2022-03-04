FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
  emacs \
  netcat \
  && rm -rf /var/lib/apt/lists/*
# TODO: Copy rudel, challenge, init script.
WORKDIR /root
COPY ./emacs.d/ /root/.emacs.d/
COPY ./challenge.sh /root
RUN chmod +x /root/challenge.sh
CMD [ "./challenge.sh" ]
