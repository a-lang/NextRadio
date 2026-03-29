# -*- coding: utf-8 -*-
#############################################
# 
# Python script for NextRadio (c.py) 
# Version: 3.0.13
#
# Created by Aladdin
# Updated by A-Lang
#
# Changes Logs:
# [2013-04-20] By A-Lang
#              Replaced the lircrc with the mplayer's subordinate mode
#              Added the audio volume control
#              Added the Mute,Power keys function
# [2013-04-21] By A-Lang
#              Fixed the zombie process created when running the command killall
#              Added a key to check the IP address
# [2013-04-27] By A-Lang
#              Fixed a few minor bugs
# [2013-04-29] By A-Lang
#              Prevents too loud sound on switching the radio channel
# [2013-05-01] By A-Lang
#              Playing an alert sound when the radio channel is not available
# [2013-05-05] By A-Lang
#              Created a branch b.py, which would support for ALSA driver
# [2013-05-25] By A-Lang
#              Changed the way of volume control
# [2013-06-01] By A-Lang
#              Added a beep audio playing when over 100% volume
# [2013-06-03] By A-Lang
#              Added the support for station list of vTuner.com
# [2013-06-08] By A-Lang
#              Changed the default audio volume to 70%
# [2013-06-15] By A-Lang
#              Added the "-cache-min" into the mplayer command (thanks Wei)
# [2013-07-25] By A-Lang
#              Added a feature 'Playing the current station number'
# [2013-09-10] By A-Lang
#              Removed the "-cache-min" into the mplayer command
# [2013-11-23] By A-Lang
#              NextRadio v2
# [2013-11-30] By A-Lang
#              Fixed the functionality to 'Play current station's ID'
# [2014-02-15] By A-Lang
#              Supported for playing Youtube Streaming
# [2014-02-22] By A-Lang
#              Added the following features in Youtobe playlist
#              Down/Right - Skip to next entry in playlist
#              Up/Left    - Skip to previous entry in playlist 
# [2014-03-01] By A-Lang
#              Fixed that Youtube playlist need to be downloaded every time
# [2014-03-08] By A-Lang
#              Have the Oo sound to prompt the Youtube playing failed
#              Disabled the loop option on playing Youtube
# [2014-03-22] By A-Lang
#              SKY.FM is supported (*.m3u)
# [2014-03-23] By A-Lang
#              Douban.FM is supported, please visit the website http://douban.fm/
# [2014-03-30] By A-Lang
#              Playing the music files in USB dongle, format MP3/MP4 is supported
# [2014-05-11] By A-Lang
#              Fixed Play/PAUSE something
# [2014-08-30] By A-Lang
#              Added the Resume Playback function for USB dongle. NextRadio will remember the last track(song) played,
#              it will resume playback from the song next time.
# [2014-11-16] By A-Lang
#              Fixed that the Oo audio is played when playing the radio but eth0 is down
# [2018-04-04] By A-Lang
#              Added the prompt when booting is done and toggle channels
#

import socket
import struct
import fcntl
import re
import time
import os
import sys 
import subprocess
import select
import commands
from subprocess import Popen, PIPE
from subprocess import check_output

i = 0
stationlist=[]
funkey = 0
power = 1
playing = 0
max_stations = 0
current_station = 0
vol_num = 70
audio_dir = "sounds/"
sockfile = '/dev/lircd'
# added by 2013-04-21
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockfd = sock.fileno()
SIOCGIFADDR = 0x8915
# added by 2014-02-16
isU2Playing = 0
U2_PlayList_Path = "/root/NextRadio/U2_PlayList"
# added by 2014-03-23
isDBFMPlaying = 0
DBFM_PlayList_Path = "/root/NextRadio/DBFM_PlayList"
# added by 2014-03-30
isUSBPlaying = 0
USB_PlayList_Path = ""

def PlayRadio(station,vol_num=100):
    global player
    global isU2Playing
    global isDBFMPlaying
    global isUSBPlaying

    if (power == 1):
        Close_Player()

        print station
        last_volnum = db_map(vol_num)

        if '.pls' in stationlist[station] or '.asx' in stationlist[station] or '.asp' in stationlist[station] or '.m3u' in stationlist[station] :
            Play_station = "mplayer -ao alsa -volume %d -subordinate -quiet -cache 256 -playlist %s & " %(last_volnum,stationlist[station].rstrip("\r\n"))
        else:
            print "Debug: Downloading the playlist"
            prompt = audio_dir + "playlist_downloading_pls_wait.mp3"
            Play_Audio(prompt, 3)
            #Play_station = "mplayer -ao alsa -volume %d -subordinate -quiet -cache 256 %s & " %(last_volnum, stationlist[station].rstrip("\r\n"))
            Play_station = "mplayer -ao alsa -volume %d -subordinate -quiet -cache 4096 -cache-min 10 %s & " %(last_volnum, stationlist[station].rstrip("\r\n"))

        if 'youtube.com' in stationlist[station] :
            force_download = 0
            if PlayU2(stationlist[station].rstrip("\r\n"), station, force_download, last_volnum):
                isU2Playing = 1     
        elif 'douban.fm' in stationlist[station] :
            force_download = 0
            if PlayDBFM(stationlist[station].rstrip("\r\n"), station, force_download, last_volnum):
                isDBFMPlaying = 1
        elif 'usb:' in stationlist[station] :
            usbPath = stationlist[station].rstrip("\r\n").split(":")[1]
            #print "Debug: usbPath: %s" %usbPath
            if PlayUSB(usbPath, "folder", station):
                isUSBPlaying = 1 
        else:
            #print Play_station
            isU2Playing = 0
            isDBFMPlaying = 0
            vol_num = last_volnum
            # 
            if Check_eth_up("eth0"):
                print "eth0 is Up...."
                player = subprocess.Popen(Play_station.split(" "), stdin=PIPE)
                
            # Checking if the Radio station is available
            Check_Player(player.pid)


def Close_Player():
    global isUSBPlaying
    try:
        if isUSBPlaying:
            RememberLastSong()
        
        player.stdin.write("quit\n")
        isUSBPlaying = 0
    except:
        pass

def Mute_Player():
    try:
        player.stdin.write("mute\n")
    except:
        pass


def Check_Player(pid, wait=5):
    prompt = audio_dir + "Oo.wav"

    time.sleep(wait)
    pid = player.pid
    status = open(os.path.join('/proc', str(pid), 'stat')).readline().split()[2]
    if status == "Z":
        os.system("mplayer -ao alsa -quiet " + prompt + " & ")

def Check_eth_up(iface):
    state = commands.getoutput("cat /sys/class/net/%s/operstate" %iface)
    if state == "up":
        #print "Up."
        return True
    else:
        #print "Down."
        return False  
        
def Get_IP(iface = 'eth0'):
    ifreq = struct.pack('16sH14s', iface, socket.AF_INET, '\x00'*14)
    try:
        res = fcntl.ioctl(sockfd, SIOCGIFADDR, ifreq)
    except:
        return None
    ip = struct.unpack('16sH2x4s8x', res)[2]
    return socket.inet_ntoa(ip)

def Play_Audio(text, mute_time=0, vol_num=70):
    if(mute_time>0):
        Mute_Player()
        
    #os.system("mplayer -ao alsa -quiet " + text + " < /dev/null & ")
    os.system("mplayer -ao alsa -volume %d -quiet %s < /dev/null & " %(vol_num, text))
    
    if(mute_time>0):
        time.sleep(mute_time)  #roughly, need detect wave file how much spend time.
        Mute_Player()

def Say_IP(ip):
    ips = ip.split('.')
    i = 0
    t = 0
    prompt = audio_dir + "the_ip_is.wav"

    for ip_number in ips:
        ip_string = str(ip_number)
        i += 1
        for digit in ip_string:
            prompt = "%s %s%s.wav" %(prompt,audio_dir,digit)
            t+=1

        if i < 4:
            prompt = "%s %sdot.wav" %(prompt,audio_dir)
            t+=1

    # Playing the audio
    Play_Audio(prompt, t+8, vol_num)
    
#==== Playing Youtube - start ====
def PlayU2(url, station_id, force_download, vol_num=70):
    global player
    Close_Player()
    
    PlayListFile= "%s.%d" %(U2_PlayList_Path, station_id)
    if (force_download or not os.path.exists(PlayListFile)) :
        print "Debug: Downloading the playlist"
        prompt = audio_dir + "playlist_downloading_pls_wait.mp3"
        Play_Audio(prompt, 5, vol_num)
        LoadU2List(url, station_id)
    #Count = int(check_output(["wc", "-l", PlayListFile]).split()[0])
    print "Debug: Start to play the U2 streaming........."
    cmd_play="mplayer -ao alsa -volume %d -subordinate -quiet -novideo -playlist %s & " %(vol_num, PlayListFile)
    player = subprocess.Popen(cmd_play.split(" "), stdin=PIPE)
    #Check_Player(player.pid, Count)
    Check_Player(player.pid, 18)
    return True
    
def LoadU2List(u2_playlist_url, station_id):
    cmd_load_playlist="bash /root/bin/load_u2_playlist.sh %s %s.%d" %(u2_playlist_url, U2_PlayList_Path, station_id)
    os.system(cmd_load_playlist)
#==== Playing Youtube - end ====    

#==== Playing Douban.FM - start ====
def PlayDBFM(url, station_id, force_download, vol_num=70):
    global player
    Close_Player()
    PlayListFile= "%s.%d" %(DBFM_PlayList_Path, station_id)
    if (force_download or not os.path.exists(PlayListFile) or file_expired(PlayListFile, 1800)):
        print "Debug: Downloading the playlist"
        prompt = audio_dir + "playlist_downloading_pls_wait.mp3"
        Play_Audio(prompt, 5, vol_num)
        LoadDBFMList(url, station_id)
    print "Debug: Start to play the Douban.FM streaming........."
    cmd_play="mplayer -ao alsa -volume %d -subordinate -quiet -novideo -playlist %s & " %(vol_num, PlayListFile)
    player = subprocess.Popen(cmd_play.split(" "), stdin=PIPE)
    #Check_Player(player.pid, Count)
    Check_Player(player.pid, 18)
    return True
    
def LoadDBFMList(dbfm_playlist_url, station_id):
    cmd_load_playlist='bash /root/bin/load_dbfm_playlist.sh "%s" %s.%d' %(dbfm_playlist_url, DBFM_PlayList_Path, station_id)
    os.system(cmd_load_playlist)
    
def file_expired(where, sec):
    now = time.time()
    file_ctime = os.path.getctime(where)
    expired = now - sec
    if file_ctime < expired:
        return True
    else:
        return False
#==== Playing Douban.FM - end ==== 

#==== Playing USB dongle - start ====
def PlayUSB(rootPath, mode, station_id=9999):
    global USB_PlayList_Path
    max_USBPlay = 0
    
    if mode == "all":
        USB_PlayList_Path = "/root/NextRadio/USB_PlayList.all"
    else:
        USB_PlayList_Path = "/root/NextRadio/USB_PlayList.%d" %station_id
    
    if(ScanFileToUSBList(rootPath, USB_PlayList_Path)):
        max_USBPlay = LoadUSBList(USB_PlayList_Path)
        if max_USBPlay > 0:
            print "Debug: Start to play the USB files........."
            print "Debug: Volume: %d" %vol_num
            PlayUSBList(USB_PlayList_Path, vol_num)
    return max_USBPlay

def PlayUSBList(playlist_path, vol_num=80): 
    global player
    Close_Player()

    songsListFile= "-loop 0 -playlist " + playlist_path                    
    cmd="mplayer -ao alsa -volume %d -subordinate -quiet -novideo %s & " %(vol_num, songsListFile)
    #player = subprocess.Popen(cmd.split(" "), stdin=PIPE)
    player = subprocess.Popen(cmd.split(" "), stdin=PIPE, stdout=PIPE)

def LoadUSBList(filename):
    sleepTime = 10
    global USBPlaylist
    global max_USBPlay
    global current_USBPlay
    USBPlaylist=[]
    current_USBPlay=0
    max_USBPlay=0
    i = 0
    fd = open (filename,"r")
    for line in fd:
        sys.stdout.write('.')
        if line[0] == '#':
            pass
        else:
            USBPlaylist.append(line)
            i = i+1
    fd.close()
    max_USBPlay=i
    if(max_USBPlay==0):
        Play_Audio("sounds/Oo.wav sounds/noplayfile.wav",5)
    print "Debug: Load %d items, last=%s" %(i, USBPlaylist[max_USBPlay-1])
    return max_USBPlay

def ScanFileToUSBList(folder, filename):
    usbPath = Get_USBPath()
    if usbPath is None:
        print "Debug: USB device not found!"
        Play_Audio("sounds/Oo.wav sounds/noplayfile.wav",5)
        return None 
    else:
        usbPath = usbPath + "/" + folder

    filelist = [os.path.join(root, name)
        for root, dirs, files in os.walk(usbPath)
        for name in files
        if name.endswith((".mp3", ".wma", ".m4a", "mp4", "flv"))]
    
    print filelist 
    
    if filelist == []:
        print "Debug: Scan No match files"
        Play_Audio("sounds/Oo.wav sounds/noplayfile.wav",5)     
        return None
        
    print "Debug: Scan %d match Files" %(len(filelist))
    
    LastSong = GetLastSong()
    if (LastSong is None):
        print "Debug: Normally Playback"
        SaveUSBList(filename, filelist)
    else:
        print "Debug: Resume Playback"
        print "Debug: LastSong is " + LastSong
        SongIndex = FindSong(filelist, LastSong)
        if (SongIndex is None):
            print "Debug: LastSong not found in filelist."
            SaveUSBList(filename, filelist)
        else:
            print "Debug: SongIndex is %d" %(SongIndex)
            print "Debug:====== RememberPlayerList ============"
            SaveUSBList(filename, ResumePlayList(filelist, SongIndex))

    return len(filelist)

def SaveUSBList(filename, USBPlaylist):    
    fd = open (filename,'w')
    for f in USBPlaylist:
        fd.write(f+"\n")
    fd.close
    return len(USBPlaylist)
    
def Get_USBPath():
    mount_output = open("/proc/mounts")
    lines = mount_output.readlines()
    for line in lines:
        words = [x.strip() for x in line.split()]
        deviceName = words[0]
        mountPath = words[1]
        if 'sdb1' in deviceName :
            return mountPath
#==== Playing USB dongle - start ====

#==== Have Mplayer to remember the song last playing ==== 
def ResumePlayList(playlist, last):
    return playlist[last:] + playlist[:last]

def Get_Result(p, cmd, expect):
    p.stdin.write(cmd + '\n') # there's no need for a \n at the beginning
    while select.select([p.stdout], [], [], 0.05)[0]: # give mplayer time to answer...
        output = p.stdout.readline()
        print("output: {}".format(output.rstrip()))
        split_output = output.split(expect + '=', 1)
        if len(split_output) == 2 and split_output[0] == '': # we have found it
            value = split_output[1]
            return value.rstrip()

def RememberLastSong():
    LastSong = Get_Result(player, 'get_file_name', 'ANS_FILENAME')
    LastSong = LastSong[1:-1]  #Strip first and last double quotes
    print("Last song:" + LastSong)
    fd = open (USB_PlayList_Path + ".last",'w')
    fd.write(LastSong + "\n")
    fd.close

def GetLastSong():
    try:
        filename = USB_PlayList_Path + ".last"
        fd = open (filename,'r')
        LastSong = fd.read()
        fd.close
        LastSong = LastSong.strip()
        print("Debug: LastSong is " + LastSong)
        return LastSong
    except:
        return None

def FindSong(filelist, songname):
    for i in xrange(len(filelist)):
        #print i, filelist[i]
        if songname in filelist[i]:
            return i
    return None

        
#=============================================================================
def Say_Digital(station, stop=0):
    #print station
    prompt = "" 
    str_station = str(station)
    i=0
    for digit in str_station:
        prompt = "%s %s%s.wav" %(prompt,audio_dir,digit) 
        
    if(stop==1):
        Mute_Player()
        #time.sleep(1)       
    #print prompt
    Play_Audio(prompt)  
    
    if(stop==1):
        time.sleep(len(str_station)+3)
        Mute_Player()
#=============================================================================

def if_volume_top(vol_num):
    prompt = audio_dir + "beep.wav"
    if vol_num > 100:
        Play_Audio(prompt)
        vol_num = 100

    return vol_num 


def db_map(vol_num):
    if vol_num >= 100:
        vol_num = 100
    elif vol_num < 100 and vol_num >= 90:
        vol_num = 91
    elif vol_num < 90 and vol_num >= 80:
        vol_num = 82
    elif vol_num < 80 and vol_num >= 70:
        vol_num = 70
    elif vol_num < 70 and vol_num >= 60:
        vol_num = 61
    elif vol_num < 60 and vol_num >= 50:
        vol_num = 52
    elif vol_num < 50 and vol_num >= 40:
        vol_num = 40
    elif vol_num < 40 and vol_num >= 30:
        vol_num = 31
    else:
        vol_num = 22

    return vol_num


def ProcessKey(current_station,vol_num):
    station_num = 0
    funckey = 0

    while 1:
        data = client_socket.recv(512)
        cmd_list = data.split( " " )
        if (cmd_list[1] == "00"):
            if (cmd_list[2] == "Blue" or cmd_list[2] == "Blue_V2"):
                #print "isU2Playing: %d" %isU2Playing
                #print "Streaming URL: %s" %(stationlist[current_station].rstrip("\r\n"))
                if isU2Playing: 
                    force_download = 1
                    PlayU2(stationlist[current_station].rstrip("\r\n"), current_station, force_download, vol_num)
                elif isDBFMPlaying:
                    force_download = 1
                    PlayDBFM(stationlist[current_station].rstrip("\r\n"), current_station, force_download, vol_num) 
            
            elif (cmd_list[2][0] == 'D'):
                station_number = funckey + int (cmd_list[2][1])
                funckey = 0
                return station_number
            elif (cmd_list[2][0] == 'R'):
                funckey = funckey + 10
            elif (cmd_list[2][0] == 'G'):
                funckey = funckey + 20
            elif (cmd_list[2][0] == 'Y'):
                funckey = funckey + 30
            elif (cmd_list[2][0] == 'B'):
                funckey = funckey + 40

            elif (cmd_list[2] == "right" or cmd_list[2] == "right_V2"):
                print "Debug: Seek Forward(right)"
                player.stdin.write("pausing_keep_force pt_step +1\n")
                
            elif (cmd_list[2] == "left" or cmd_list[2] == "left_V2"):
                print "Debug: Seek Backward(left)"
                player.stdin.write("pausing_keep_force pt_step -1\n")
                
            elif (cmd_list[2] == "down" or cmd_list[2] == "down_V2"):
                print "Debug: Seek Forward(down)"
                player.stdin.write("pausing_keep_force pt_step +1\n")
                
            elif (cmd_list[2] == "up" or cmd_list[2] == "up_V2"):
                print "Debug: Seek Backward(up)"
                player.stdin.write("pausing_keep_force pt_step -1\n")

            elif (cmd_list[2] == "chUp" or cmd_list[2] == "chUp_V2"):
                return current_station - 1

            elif (cmd_list[2] == "chDown" or cmd_list[2] == "chDown_V2"):
                return current_station + 1

            elif (cmd_list[2] == "volUp" or cmd_list[2] == "volUp_V2"):
                player.stdin.write("volume +47\n")
                vol_num += 3
                vol_num2 = if_volume_top(vol_num)
                return "volx%d"%vol_num2

            elif (cmd_list[2] == "volDown" or cmd_list[2] == "volDown_V2"):
                player.stdin.write("volume -47\n")
                vol_num -= 3
                return "volx%d"%vol_num

            elif (cmd_list[2] == "power"):
                funckey = 0
                return 1200
                
            elif (cmd_list[2] == "play"):
                return 1201    
         
            elif (cmd_list[2] == "mute"):
                player.stdin.write("mute\n")
                
            elif cmd_list[2] == "info":
                ip = Get_IP('eth0')
                if ip is None:
                    ip = "0.0.0.0"
                # Playing ip
                Say_IP(ip)
                
            elif cmd_list[2] == "search":
                Say_Digital(current_station,1)


fd = open ("/root/NextRadio/upload/radio.txt","r")
for line in fd:
    msg = re.search('^#',line)
    sys.stdout.write('.')
    if msg:
        pass
    else:
        stationlist.append(line)
        i = i+1
fd.close()

max_stations = i-1
print "\n" + stationlist[max_stations]
#PlayRadio(current_station,vol_num)
prompt = audio_dir + "bootup_is_done.mp3"
Play_Audio(prompt, 3)

client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
client_socket.connect(sockfile);

                

while 1:
    re = ProcessKey(current_station,vol_num)
    
    if (re < -1):
        continue
    elif (re == 1200):
        if (power == 1):
            power = 0
            Close_Player()
        else:
            power = 1
            PlayRadio(current_station,vol_num)
        continue
    elif (re == 1201):
        if isUSBPlaying:
            print "Debug: Pressed Pause !"
            player.stdin.write("pause\n")
        else:  
            if PlayUSB("/", "all"):
                isUSBPlaying = 1
            else:
                isUSBPlaying = 0
        continue     
    elif isinstance(re, str):
        if "volx" in re:
            #print re[4:]
            vol_num = int(re[4:])
        continue
    else:
        station = re 
        if (station == current_station):
            continue
        elif (station > max_stations + 1):
            continue
        elif (station == max_stations + 1):
            station = 0;
        elif (station == -1):
            station = max_stations

    if power == 1 and station >= 0 and station <= max_stations :
        current_station = station
        PlayRadio(station,vol_num)
   
