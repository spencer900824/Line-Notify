#!/bin/bash
# delete old image
sudo docker stop line-notify 
sudo docker rm line-notify
sudo docker rmi line-notify:latest
# build
sudo docker build -t line-notify .
# run
lt --port 5001 &
sudo docker run --name line-notify -p 5001:5001 line-notify > run_log
