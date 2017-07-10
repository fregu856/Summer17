raspivid -t 0 -w 1280 -h 720 -fps 20 -o - | nc -l -p 8080
