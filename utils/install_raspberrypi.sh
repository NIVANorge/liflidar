#!/bin/bash

# exit on error
set -e

# raspberry pi doesn't ask for a password by default
sudo apt update && sudo apt -y full-upgrade

sudo apt install -y \
    vim \
    python3-pyqt5

sudo apt-get install --no-install-recommends -y \
  xserver-xorg-video-all \
  xserver-xorg-input-all \
  xserver-xorg-core \
  xinit \
  x11-xserver-utils

sudo apt autoremove -y
sudo apt clean -y
