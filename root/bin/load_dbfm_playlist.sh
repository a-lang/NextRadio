#!/bin/bash
# Don't modify this script

DBFM_PlayList_URL=$1
DBFM_PlayList_PATH=$2

[ -z $1 ] || [ -z $2 ] && exit 1

echo "Downloading the Douban.FM playlist, please be patient...."
curl $DBFM_PlayList_URL | sed 's/\\//g' | awk -F"," '{for(i=1;i<=NF;i++){print $i}}' | sed -n '/url/p' | sed -e 's/\"//g' -e 's/^url://g' > $DBFM_PlayList_PATH

sync;sync

