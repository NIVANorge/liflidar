#!/bin/bash

sudo pigpiod

source /home/pi/env/bin/activate
python /home/pi/liflidar/gui.py > /home/pi/log.out 2>&1
