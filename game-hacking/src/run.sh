#!/usr/bin/env bash

HOSTNAME="${GAME_HOSTNAME:-ws://localhost:8124}"

(echo "const HOSTNAME='${HOSTNAME}';"; cat /root/client/game-obfuscated.js) > /root/client/game.js

pushd /root/client/
python3 -m http.server 8123 &
popd

pushd /root/server/
python3 server.py
