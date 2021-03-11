#!/bin/bash

sudo python3 /home/pi/WATERs/src/waterSensor.py

chk_scan=`ps -eaf | grep "waterControl" | wc -l`
if [ $chk_scan -eq 0 ]
        then
        sudo python3 /home/pi/WATERs/src/waterControl.py &
fi

chk_scan=`ps -eaf | grep "waterMqtt" | wc -l`
if [ $chk_scan -eq 0 ]
        then
        sudo python3 /home/pi/WATERs/src/waterMqtt.py &
fi

chk_scan=`ps -eaf | grep "fbcp" | wc -l`
if [ $chk_scan -eq 0 ]
        then
        fbcp &
fi

exit
