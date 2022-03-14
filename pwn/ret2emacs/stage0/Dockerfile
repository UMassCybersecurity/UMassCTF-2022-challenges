FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
  autoconf \
  build-essential \
  git \
  libgtk-3-dev \
  libtiff5-dev \
  libgif-dev \
  libgmp-dev \
  libjpeg-dev \
  libpng-dev \
  libxpm-dev \
  libncurses-dev \
  libsixel-dev \
  texinfo \
  && rm -rf /var/lib/apt/lists/*
COPY ./emacs/ /tmp/emacs/
WORKDIR /tmp/emacs/
RUN sed -i 's/SIGSTKSZ/1024/' src/sysdep.c
RUN rm -rf .git
RUN ./autogen.sh
RUN ./configure --with-gnutls=ifavailable --with-modules --with-libgmp --with-json --with-threads --with-wide-int --with-zlib --with-x-toolkit=gtk3 --with-dumping=unexec
RUN make
RUN make DESTDIR=./install install
RUN cp ./lib-src/emacsclient ./install/usr/local/bin/
RUN make install
COPY ./sixel-el/ /tmp/sixel-el/
WORKDIR /tmp/sixel-el/
RUN make

FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
  make \
  libgtk-3-0 \
  libgif7 \
  libxft2 \
  libice6 \
  libsm6 \
  libxpm4 \
  libsixel-bin \
  netcat \
  && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y \
  xvfb \
  && rm -rf /var/lib/apt/lists/*
COPY --from=0 /tmp/emacs/install/ /tmp/emacs/
WORKDIR /tmp/emacs/
RUN yes | cp -vrp * /
WORKDIR /root
COPY --from=0 /tmp/sixel-el/sixmacs.so /root/sixmacs.so
COPY --from=0 /tmp/sixel-el/sixmacs.el /root/sixmacs.el
COPY ./emacs.d/ /root/.emacs.d/
COPY ./challenge.sh /root
RUN chmod +x /root/challenge.sh
CMD [ "./challenge.sh" ]
