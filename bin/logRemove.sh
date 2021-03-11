#!/bin/bash
cd /home/pi/WATERs/bin/logs
find ./*.log -ctime +30 -exec sudo rm -f {} \;
find ./*.csv -ctime +365 -exec sudo rm -f {} \;
