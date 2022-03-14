FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
  build-essential \
  emacs \
  libsixel-dev \
  && rm -rf /var/lib/apt/lists/*
COPY ./emacs/ /tmp/emacs/
WORKDIR /tmp/emacs/
RUN sed -i 's/SIGSTKSZ/1024/' src/sysdep.c
RUN ./autogen.sh
RUN ./configure --with-modules --with-libgmp --with-json --with-threads --with-wide-int --with-zlib --with-x-toolkit=gtk3 --with-dumping=unexec
RUN make
COPY ./sixel-el/ /tmp/sixel-el/
WORKDIR /tmp/sixel-el/
RUN make

FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
  emacs \
  libsixel-bin \
  netcat \
  && rm -rf /var/lib/apt/lists/*
# TODO: Copy rudel, challenge, init script.
WORKDIR /root
COPY --from=0 /tmp/sixel-el/sixmacs.so /root/sixmacs.so
COPY --from=0 /tmp/sixel-el/sixmacs.el /root/sixmacs.el
COPY ./emacs.d/ /root/.emacs.d/
COPY ./challenge.sh /root
RUN chmod +x /root/challenge.sh
CMD [ "./challenge.sh" ]
