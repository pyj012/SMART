#!/bin/bash
while true; do
    # error_count=`tail "/var/log/syslog" | grep -c "nvargus-daemon\|Error InvalidState\|Session.cpp"`
    #error_count=`tail -100 "/var/log/syslog" | grep -c "nvargus-daemon.*Error"`
    error_count1=`tail -100 "/var/log/syslog" | grep -c "nvargus-daemon.*Error InvalidState.*Session.cpp"`
    # error_count2=`tail -100 "/var/log/syslog" | grep -c "SCF: Error Timeout:.*Session.cpp"`
    error_count2=`tail -100 "/var/log/syslog" | grep -c "SCF: Error Timeout:.*"`
    error_count=$((error_count1+error_count2))

    if (( ${error_count} > 0 )); then
        echo "RUN - Kill nvargus-daemon and gst-launch process"
        cp /var/log/syslog /home/bready/syslog
        # systemctl restart nvargus-daemon
        killall -9 gst-launch-1.0
        truncate -s 0 /var/log/syslog
        sleep 3
    else
        echo "RUN - Not Detected Error"
    fi

    process_count=`pgrep -c gst-launch-1.0`
    if (( ${process_count} == 0 )); then
        gst-launch-1.0 libcamerasrc ! video/x-raw,width=640,height=480,framerate=30/1 ! videoconvert ! jpegenc ! multipartmux ! tcpserversink host=0.0.0.0 port=5000
        #gst-launch-1.0 nvarguscamerasrc sensor-id=0 ! 'video/x-raw(memory:NVMM),width=3264, height=2464, framerate=10/1, format=NV12' ! nvvidconv flip-method=2 interpolation-method=4 ! 'video/x-raw, width=406, height=306' ! videoconvert ! nvjpegenc ! multipartmux ! tcpserversink host=0.0.0.0 port=5000 &
        echo "RUN - gst-launch-1.0 is restarted"
    fi
    sleep 0.1;
done

