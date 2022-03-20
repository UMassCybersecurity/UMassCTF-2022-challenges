#!/usr/bin/env bash

pushd /root/client/
python3 -m http.server 8080 &
popd

pushd /root/server/
python3 server.py
