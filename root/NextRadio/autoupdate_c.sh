#!/bin/bash
# Autoupdate script for NextRadio
# file: autoupdate_c.sh
# author: A-Lang
# updated: 2013-11-24
#
WGET='/usr/bin/wget --no-check-certificate -N'
WORKDIR="/tmp/nextradio_$$"
#DIR=`pwd`

mkdir -p $WORKDIR || exit 1
cd $WORKDIR

# Checking for the current version
CURRENT_VER=""
RELEASE="/root/NextRadio/RELEASE"
[ -r $RELEASE ] && {
    . $RELEASE &>/dev/null
	 CURRENT_VER="$VERSION"
}

# Start to blink the LED
/root/bin/led.sh b
/root/bin/led.sh r
/root/bin/led.sh b
/root/bin/led.sh blink &
led_pid=$!

# Getting the last version number
URL='http://www.openfoundry.org/of/download_path/nextradio/last_release/last_release_v2'
LAST_VER=""
$WGET $URL
[ $? = 0 ] && {
    . $WORKDIR/last_release_v2 &>/dev/null
	 LAST_VER="$LAST_VERSION"
}

DO_UPDATE=0
PATCH_FILE=""
if [ "$CURRENT_VER" == "$LAST_VER" ]; then
   echo "No need of update, continuing."
   
elif [ -z "$CURRENT_VER" ] || [ -z "$LAST_VER" ]; then
   echo "It seems there is something wrong with checking the version, continuing."

else
   # Getting the latest patch file
   URL='http://www.openfoundry.org/of/download_path/nextradio/Last_Patch_Rootfs/patch_nextradio_v2_rootfs.tgz'
   PATCH_FILE="${URL##*/}"
   $WGET $URL
   [ $? = 0 ] && DO_UPDATE=1
fi

if [ "$DO_UPDATE" -eq "1" ]; then
    echo "Updating the NextRadio."
    [ -f $PATCH_FILE ] && tar xzf $PATCH_FILE -C /
    [ $? = 0 ] && echo "--> Done"
fi


# Stop to blink the LED
kill -9 $led_pid
wait $led_pid 2>/dev/null
sleep 2
/root/bin/led.sh b

# Cleaning up the unused files
rm -rf $WORKDIR

#echo "CURRENT_VER=$CURRENT_VER"
#echo "LAST_VER=$LAST_VER"
#echo "DO_UPDATE=$DO_UPDATE"
#echo "PATCH_FILE=$PATCH_FILE"
