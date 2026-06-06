#!/usr/bin/env bash
# exit on error
set -o errexit

STORAGE_DIR=/opt/render/project/.render

if [ ! -d "$STORAGE_DIR/chrome" ]; then
  echo "...Downloading Chrome..."
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  wget https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.94/linux64/chrome-linux64.zip
  unzip chrome-linux64.zip
  ln -s $STORAGE_DIR/chrome/chrome-linux64/chrome /opt/render/project/src/chrome
  cd /opt/render/project/src
else
  echo "...Chrome already installed..."
  ln -s $STORAGE_DIR/chrome/chrome-linux64/chrome /opt/render/project/src/chrome
fi

pip install -r requirements.txt
