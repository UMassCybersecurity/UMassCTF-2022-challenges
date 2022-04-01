#!/usr/bin/env bash

set -e

# Kill the container after 30 seconds have elapsed.
{
  set -e
  sleep 30
  kill $$
} &
trap "pkill emacs" EXIT

# Start the Emacs daemon.
emacs --daemon >/dev/null 2>/dev/null

# Spawn a fake X11 frame attached to the Emacs session.
Xvfb :99 -screen 0 640x480x8 -nolisten tcp >/dev/null 2>/dev/null &
export DISPLAY=:99

# Load the vulnerable Emacs module.
emacsclient --eval "(load-file \"/root/sixmacs.so\")" >/dev/null 2>/dev/null
# expect "t"
emacsclient --eval "(load-file \"/root/sixmacs.el\")" >/dev/null 2>/dev/null
# expect "t"

# # Inject the flag.
emacsclient --eval "(progn (set-buffer (generate-new-buffer \"*flag*\")) (insert \"UMASS{n0T_4_DUnk_0n_3M4c2_By_4nY_M34n2.._n3Xt_Y34r_will_b3_n30V1M}\") (buffer-string))" >/dev/null 2>/dev/null

# # Start the Rudel server, connect to it, and publish *scratch*.
emacsclient --eval "(progn (find-file \"/root/.emacs.d/elpa/rudel-0.3.2/rudel-loaddefs.el\") (eval-buffer))" >/dev/null 2>/dev/null
emacsclient --eval "(rudel-host-session \`(:transport-backend ,(rudel-backend-choose 'transport (lambda (backend) (rudel-capable-of-p backend 'listen))) :protocol-backend ,(rudel-backend-choose 'protocol (lambda (backend) (rudel-capable-of-p backend 'host))) :address \"localhost\" :port 6522 :encryption nil))" >/dev/null 2>/dev/null
emacsclient --eval "(rudel-join-session \`(:transport-backend ,(rudel-backend-choose 'transport (lambda (backend) (rudel-capable-of-p backend 'listen))) :protocol-backend ,(rudel-backend-choose 'protocol (lambda (backend) (rudel-capable-of-p backend 'host))) :color \"Red\" :username \"jakob\" :global-password \"\" :user-password \"\" :host \"localhost\" :port 6522 :encryption nil))" >/dev/null 2>/dev/null
emacsclient --eval "(rudel-publish-buffer (get-buffer \"*scratch*\"))" >/dev/null 2>/dev/null
emacsclient -c --eval "(progn (set-buffer \"*scratch*\") (advice-add 'rudel-update-author-overlay-after-insert :after #'sixplayground-on-post-command))" >/dev/null 2>/dev/null &

# Tunnel to Rudel over stdin/stdout.
nc localhost 6522
