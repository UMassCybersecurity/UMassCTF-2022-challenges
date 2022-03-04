#!/usr/bin/env bash

set -e

# Start the Emacs daemon.
emacs --daemon >/dev/null 2>/dev/null

# Start the Rudel server, connect to it, and publish *scratch*.
emacsclient --eval "(progn (find-file \"/root/.emacs.d/elpa/rudel-0.3.2/rudel-loaddefs.el\") (eval-buffer))" >/dev/null 2>/dev/null
emacsclient --eval "(make-thread (lambda () (rudel-host-session \`(:transport-backend ,(rudel-backend-choose 'transport (lambda (backend) (rudel-capable-of-p backend 'listen))) :protocol-backend ,(rudel-backend-choose 'protocol (lambda (backend) (rudel-capable-of-p backend 'host))) :address \"localhost\" :port 6522 :encryption nil))))" >/dev/null 2>/dev/null
sleep 2
emacsclient --eval "(make-thread (lambda () (rudel-join-session \`(:transport-backend ,(rudel-backend-choose 'transport (lambda (backend) (rudel-capable-of-p backend 'listen))) :protocol-backend ,(rudel-backend-choose 'protocol (lambda (backend) (rudel-capable-of-p backend 'host))) :color \"Red\" :username \"jakob\" :global-password \"\" :user-password \"\" :host \"localhost\" :port 6522 :encryption nil))))" >/dev/null 2>/dev/null
sleep 2
emacsclient --eval "(rudel-publish-buffer (get-buffer \"*scratch*\"))" >/dev/null 2>/dev/null

# Tunnel to Rudel over stdin/stdout.
nc localhost 6522
