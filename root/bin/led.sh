#!/bin/bash
# This script is used to control the LED on NextPBX
# Written by A-Lang 2013/11/10

ioroot=/sys/class/gpio
iored=$ioroot/gpio5
ioblue=$ioroot/gpio4
on="high"
off="in"

cd $ioroot
#if gpio4 not exist, create it.
if test ! -d $ioblue; then
    echo "4" > $ioroot/export
fi

#if gpio5 not exist, create it.
if test ! -d $iored; then
    echo "5" > $ioroot/export
fi

valred=`cat $iored/value`
valblue=`cat $ioblue/value`

red()
{
    if test $valred -eq 0; then
        echo $on > $iored/direction
    fi
    if test $valblue -eq 1; then
        echo $off > $ioblue/direction
    fi
}

blue()
{
    if test $valred -eq 1; then
        echo $off > $iored/direction
    fi
    if test $valblue -eq 0; then
        echo $on > $ioblue/direction
    fi
}

purple()
{
    if test $valred -eq 0; then
        echo $on > $iored/direction
    fi
    if test $valblue -eq 0; then
        echo $on > $ioblue/direction
    fi
}

off()
{
    if test $valred -eq 1; then
        echo 0 > $iored/value
    fi
    if test $valblue -eq 1; then
        echo 0 > $ioblue/value
    fi
}

blink()
{
    if test $valred -eq 1; then
        while true
        do
            echo 1 > $iored/value
            sleep 0.5
            echo 0 > $iored/value
            sleep 0.5
        done
    elif test $valblue -eq 1; then
        while true
        do
            echo 1 > $ioblue/value
            sleep 0.5
            echo 0 > $ioblue/value
            sleep 0.5
        done
    fi
}

case $1 in
    "r")
        red
        ;;

    "b")
        blue
        ;;

    "p")
        purple
        ;;

    # delete gpio4 gpio5
    "d")
        echo 4 > $ioroot/unexport
        echo 5 > $ioroot/unexport
        ;;

    "o")
        off
        ;;

    "blink")
        blink
        ;;

    *)
        echo "use $0 [r:red/b:blue/p:purple/o:off/d:delete/blink:blink]"
        ;;
esac
