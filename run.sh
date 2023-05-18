#!/bin/bash

# build
sudo docker build -t line-notify .
# run
sudo docker run -d -p 5001:5001 line-notify && lt --port 5001