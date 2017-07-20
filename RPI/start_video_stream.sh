raspivid -t 0 -w 1280 -h 720 -hf -vf -fps 20 -o - | nc -l -p 8080
