#!/bin/bash
# Don't modify this script

U2_PlayList_URL=$1
U2_PlayList_PATH=$2

[ -z $1 ] || [ -z $2 ] && exit 1

/root/bin/youtube-dl -U
sync;sync

echo "Downloading the Youtube playlist, please be patient...."
/root/bin/youtube-dl -g $U2_PlayList_URL > $U2_PlayList_PATH
sync;sync

[ -s $U2_PlayList_PATH ] && sed -i 's/^https/http/g' $U2_PlayList_PATH
sync;sync
