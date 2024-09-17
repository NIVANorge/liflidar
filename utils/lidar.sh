#!/bin/bash

sudo pigpiod

source /home/pi/pyenv/bin/activate
python /home/pi/liflidar/main.py > /home/pi/log.out 2>&1
