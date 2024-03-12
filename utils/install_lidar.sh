#!/bin/bash

# exit on error
set -e

# it will change an owner to root
# sudo cp lidar.service /lib/systemd/system/

# create a python environment and use raspberry pi system
# preinstalled pyqt, numpy, etc libraries
python -m venv --system-site-packages $HOME/pyenv

# activate the python environment
source $HOME/pyenv/bin/activate
# install python modules into the venv
python -m pip install --upgrade pip
python -m pip install -e ../.

# sudo systemctl enable lidar.service
