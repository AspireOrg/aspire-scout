#!/bin/bash

echo "Starting..."

# nvm install v13.6.0
# npm install -g sass
export PATH="$PATH:/root/.nvm/versions/node/v13.6.0/bin/"

# rm -R /usr/local/lib/python3.5/dist-packages/webassets
# git clone https://github.com/miracle2k/webassets.git /usr/local/lib/python3.5/dist-packages/webassets
# cd /usr/local/lib/python3.5/dist-packages/webassets
# /usr/bin/python3.5 setup.py install

mkdir -p /scout/logs/
cd /scout

echo "Running pip install..."
/usr/bin/pip3.5 install -r requirements.txt

echo "Running scout..."
/usr/bin/python3.5 run.py

echo "Closed"