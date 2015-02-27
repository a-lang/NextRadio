import urllib2
import commands
import time
import os

INTERVAL=1

def internet_on():
    try:
        response=urllib2.urlopen('http://www.google.com', timeout=1)
        return True
    #except urllib2.URLError as err: pass
    except: pass
    return False

def eth_up(iface):
    state = commands.getoutput("cat /sys/class/net/%s/operstate" %iface)
    if state == "up":
        #print "Up."
        return True
    else:
        #print "Down."
        return False

while True:
    if eth_up("eth0"):
        if internet_on():
            #print "Connected."
            os.system('/root/bin/led.sh b')
        else:
            #print "Disconnected."
            os.system('/root/bin/led.sh r')
    else:
        #print "Disconnected."
        os.system('/root/bin/led.sh r')
    time.sleep(INTERVAL)
