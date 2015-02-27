#!/usr/bin/python
#

import os, sys

# Checking and downloading the latest updates for NextRadio
url = 'http://www.openfoundry.org/of/download_path/nextradio/autoupdate/autoupdate_c.sh'
auto_update = 1     #1:yes, 0:no

wkdir = os.path.abspath(os.path.dirname(sys.argv[0]))
file_name = url.split('/')[-1]
os.chdir(wkdir)
if auto_update == 1:
  r = os.system("wget --no-check-certificate -N -T 10 -t 1 %s" %url)
  if r == 0:
     print "The latest file downloaded: " + wkdir + "/" + file_name
     print "Now performing the autoupdate..."
     os.system("bash "+file_name)

# Starting the Radio
print "Starting the Radio..."
os.system("python c.py")

