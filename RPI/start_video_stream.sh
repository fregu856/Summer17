raspivid -t 0 -w 640 -h 360 -hf -vf -fps 20 -o - | nc -l -p 8080
