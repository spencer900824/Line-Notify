#!/bin/bash

sudo yum update -y

# install git
sudo yum install git -y

# Install docker
sudo amazon-linux-extras install docker -y
sudo service docker start

# Install nodejs
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
. ~/.nvm/nvm.sh
nvm install 16

# Install localtunnel
npm install -g localtunnel

# clone github repo
git clonehttps://github.com/spencer900824/Line-Notify.git