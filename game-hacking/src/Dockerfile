FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update \
    && apt-get install -y python3 python3-pip npm \
    && rm -rf /var/lib/apt/lists/*
RUN npm install -g javascript-obfuscator
COPY ./server /root/server
RUN pip install -r /root/server/requirements.txt
COPY ./client /root/client
WORKDIR /root/client
RUN javascript-obfuscator game.js --rename-globals=true
COPY ./run.sh /root/run.sh
RUN chmod +x /root/run.sh
CMD /root/run.sh
