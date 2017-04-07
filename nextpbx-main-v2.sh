#!/bin/bash
# File: nextpbx-main.sh
# Author: A-Lang
# Updated by 2013-11-16
#
export PATH="/usr/bin:/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/sbin"
CURDIR=`pwd`
URL_nextpbx="http://www.openfoundry.org/of/download_path/nextpbx/current/target_NextPBX_by_osslab_current.tgz"
URL_nextradio_alsa="http://www.openfoundry.org/of/download_path/nextradio/NextRadio_Rootfs/nextradio_rootfs-alsa.tgz"
URL_nextradio_v2="http://www.openfoundry.org/of/download_path/nextradio/NextRadio_Rootfs/nextradio_v2_rootfs.tgz"

#=== functions ===
exit_notok(){
   echo -e "\n[Error]: $1"
   echo "[Info]:Should you ran into any problems, you could email to us at asterisk-tw@googlegroups.com"
   exit 1
}

echo_ok(){
   echo -e "\n[Info]:$1"
}

main_menu(){
   clear
   echo "Please Select the Project name that you want to install:"
   echo "(1) NextPBX - An IP-PBX Telephony System"
   echo "(2) NextRadio for ALSA - An Internet Radio System"
   echo "(3) NextRadio V2 - An Internet Radio System(New)"
   echo ""
   echo -n "Please Input the item NO.: "
   read selected
}

main_menu
case "$selected" in
   1)
     PKGNAME="nextpbx"
     GET_URL="$URL_nextpbx"
   ;;
   2)
     PKGNAME="nextradio"
     GET_URL="$URL_nextradio_alsa"
   ;;
   3)
     PKGNAME="nextradio_v2"
     GET_URL="$URL_nextradio_v2"
   ;;
   *)
     exit_notok "Wrong choice!"
esac

#=== Downloading the latest firmware ===
GET_FILENAME=${GET_URL##*/}
[ -r $CURDIR/$GET_FILENAME ] && rm $CURDIR/$GET_FILENAME
echo_ok "Downloading the file needed..."
wget $GET_URL
[ $? != 0 ] && exit_notok "$GET_FILENAME failed to download."

#=== Check some things ===
[ -r $CURDIR/$GET_FILENAME ] || exit_notok "File $GET_FILENAME not found."
[ -r /target.tgz ] || exit_notok "File /target.tgz not found."

#=== Check the mount moint for root ===
SDA1_MOUNT_POINT=`df -h | grep "/dev/sda1" | awk '{print $6}'`
if [ "$SDA1_MOUNT_POINT" = "/" ]; then
    # Get the partition id of the /dev/sdbX
    SDBX=$(cat /proc/partitions | awk '{print $4}' | grep "sdb[2-9]")
    for parts in $SDBX;do
        id=${parts#sdb}
        fdisk_in="
        $fdisk_in
        d
        $id
        "
    done

    fdisk /dev/sdb <<EOF
$fdisk_in
n
p
2


p
w
EOF

    #=== Format /dev/sdb2 ===
    SDB2_MOUNT_POINT=`df -h | grep "/dev/sdb2" | awk '{print $6}'`
    if [ "$SDB2_MOUNT_POINT" = "" ];then
        # Start to blink the LED
        /root/bin/led.sh b
        /root/bin/led.sh r
        /root/bin/led.sh b
        /root/bin/led.sh blink &
        led_pid=$!

        echo_ok "Formating /dev/sdb2, please be patient..."
        mkfs.ext2 -j -b 4096 -m 2 /dev/sdb2
        [ $? != 0 ] && exit_notok "Formating the /dev/sdb2 failed."

        # Stop to blink the LED
        kill -9 $led_pid
        wait $led_pid 2>/dev/null
        sleep 2
        /root/bin/led.sh b
    else
        exit_notok "The /dev/sdb2 has been mounted,  please umount it then re-run again."
    fi
fi

#=== Install the latest firmware ===
case "$PKGNAME" in
   nextpbx)
        mount /dev/sdb2 /mnt_system
        [ $? != 0 ] && exit_notok "Mounting the /dev/sdb2 failed. If it existed please umount it then re-run again."

        # Start to blink the LED
        /root/bin/led.sh b
        /root/bin/led.sh r
        /root/bin/led.sh b
        /root/bin/led.sh blink &
        led_pid=$!

        echo_ok "Recovering the factory firmware, this may take 1-2 mins..."
        tar xzf /target.tgz -C /
        [ $? != 0 ] && exit_notok "Recovering firmware failed."
        sync;sync;sync

        echo_ok "Installing the latest NextPBX firmware, this may take 1-2 mins..."
        tar xzf $CURDIR/$GET_FILENAME -C /mnt_system
        [ $? != 0 ] && exit_notok "Installing NextPBX firmware failed."

        # Stop to blink the LED
        kill -9 $led_pid
        wait $led_pid 2>/dev/null
        sleep 2
        /root/bin/led.sh b

        sync;sync;sync
        umount /mnt_system
        ;;

    nextradio)
        mount /dev/sdb2 /mnt_system
        [ $? != 0 ] && exit_notok "Mounting the /dev/sdb2 failed. If it existed please umount it then re-run again."

        # Start to blink the LED
        /root/bin/led.sh b
        /root/bin/led.sh r
        /root/bin/led.sh b
        /root/bin/led.sh blink &
        led_pid=$!

        echo_ok "Installing the latest NextRadio firmware, this may take 3-4 mins..."
        tar xzf $CURDIR/$GET_FILENAME -C /mnt_system
        [ $? != 0 ] && exit_notok "Installing NextRadio firmware failed."

        # Stop to blink the LED
        kill -9 $led_pid
        wait $led_pid 2>/dev/null
        sleep 2
        /root/bin/led.sh b

        sync;sync;sync
        umount /mnt_system
        ;;

    nextradio_v2)
        mount /dev/sdb2 /mnt_system
        [ $? != 0 ] && exit_notok "Mounting the /dev/sdb2 failed. If it existed please umount it then re-run again."

        # Start to blink the LED
        /root/bin/led.sh b
        /root/bin/led.sh r
        /root/bin/led.sh b
        /root/bin/led.sh blink &
        led_pid=$!

        echo_ok "Installing the latest NextRadio V2 firmware, this may take 3-4 mins..."
        tar xzf $CURDIR/$GET_FILENAME -C /mnt_system
        [ $? != 0 ] && exit_notok "Installing NextRadio firmware failed."
        mkdir /mnt_system/proc /mnt_system/sys /mnt_system/mnt /mnt_system/media

        # Stop to blink the LED
        kill -9 $led_pid
        wait $led_pid 2>/dev/null
        sleep 2
        /root/bin/led.sh b

        sync;sync;sync
        umount /mnt_system
        ;;
esac

echo
echo_ok "Congratulation! Installation Completed."
echo_ok "Please Power Off your nextvod unit then re-start it."


