#!/bin/bash

# build
sudo docker build -t line-notify .
# run
lt --port 5001 &
sudo docker run -p 5001:5001 line-notify > run_log
