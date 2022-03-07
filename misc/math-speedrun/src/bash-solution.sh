exec 3<>/dev/tcp/127.0.0.1/8085;

head -7 <&3

awk '{print $1}' >&3;
