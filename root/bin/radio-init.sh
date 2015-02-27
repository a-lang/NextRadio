#!/bin/bash

echo "Sync clock..." > /tmp/cron_local.log
ntpdate time.stdtime.gov.tw

echo "Fix for LIRC....." >> /tmp/cron_local.log
# fix for Lirc
ln -s /dev/lirc0 /dev/lirc

echo "Startup the Internet Radio" >> /tmp/cron_local.log
# Startup the Internet Radio
python /root/NextRadio/radio-start_c.py &
su - -c "python /root/NextRadio/httpserver_droopy.py &"
python /root/bin/watchdog.py &

