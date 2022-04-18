#!/bin/bash

#sudo teamviewer info | grep "TeamViewer ID" > teamviewerID.txt

./waterAgent &

#sudo python3 /home/pi/WATERs/src/waterControl.py &
sudo python3 /home/pi/WATERs/src/waterSerial.py &
sudo python3 /home/pi/WATERs/src/waterMqtt.py &

exit
