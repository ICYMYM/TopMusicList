#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
MusicList of Baidu:
    http://tingapi.ting.baidu.com/v1/restserver/ting? \
    from=android&version=4.4.0&method=baidu.ting.billboard.billList&format=json&type=6 \
    &offset=0&size=100&fields=song_id,title,author,album_title,pic_big,pic_small,havehigh,all_rate,charge

type:
1：新歌
2：热歌
31：好声音
21：欧美金曲
24：影视金曲
23：情歌对唱
25：网络歌曲
22：经典老歌
11：摇滚榜
6：ktv榜
8：Billboard
18：Hito中文榜
7：叱咤歌曲榜
20：华语金曲榜

"""

from random import choice
import MySQLdb
import demjson
import htmlentitydefs
import os
import re
import socket
import sys
import time
import urllib2
import xml.etree.ElementTree as ET
import HTMLParser

reload(sys)
sys.setdefaultencoding("utf8")

socket.setdefaulttimeout(120)

USER_AGENTS = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en) AppleWebKit/419 (KHTML, like Gecko) Safari/419.3',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.83 Safari/537.1',
    'Mozilla/5.0 (Windows NT 6.1; rv:14.0) Gecko/20100101 Firefox/14.0.1'
]

SOURCE = 'baidu'

TYPE = [1,2,31,21,24,23,25,22,11,6,8,18,7,20]

TYPE_MAP ={1:"新歌",
           2:"热歌",
           31:"好声音",
           21:"欧美金曲",
           24:"影视金曲",
           23:"情歌对唱",
           25:"网络歌曲",
           22:"经典老歌",
           11:"摇滚榜",
           6:"ktv榜",
           8:"Billboard",
           18:"Hito中文榜",
           7:"叱咤歌曲榜",
           20:"华语金曲榜"}

defaultFilePath = './MusicList_baidu.lst'


def warning(text):
    return '\033[93m' + text + '\033[0m'


def error(text):
    return '\033[91m' + text + '\033[0m'


def getPage(url, referer=''):
    response = ''
    for i in range(3):
        request = urllib2.Request(url)
        request.add_header("User-Agent", choice(USER_AGENTS))
        if referer:
            request.add_header("Refeer", referer)
        try:
            response = urllib2.urlopen(request)
            if response:
                result = response.read()
                response.close()
                return result
        except Exception as e:
            if response:
                response.close()
    return ''

def getMusicListSong_baidu(typeid,offset=0,size=100):
    hotmusic_url = 'http://tingapi.ting.baidu.com/v1/restserver/ting?from=android&version=4.4.0&method=baidu.ting.billboard.billList&format=json&type={0}&offset={1}&size={2}&fields=song_id,title,author,album_title,pic_big,pic_small,havehigh,all_rate,charge'
    page = getPage(hotmusic_url.format(typeid,offset,size))

    if not page:
        print error("get page error")
        print error(hotmusic_url.format(typeid,offset,size))
        return

    songinfo_list = list()
    try:
        data = demjson.decode(page)
    except Exception as e:
        print error(e)

    song_list = data.get('song_list',list())
    if not song_list:
        #print warning('End of Musiclist')
        return songinfo_list

    htmlP = HTMLParser.HTMLParser() #Decode HTML entities
    for song in song_list:
        songid = song.get('song_id','')
        songName = htmlP.unescape(song.get('title',''))
        artistName = htmlP.unescape(song.get('author',''))
        if songid and songName and artistName:
            if artistName=='#124':
                artistName = ''
            songinfo_list.append([songid,songName,artistName])

    return songinfo_list


def writeToFile(outfile, songinfo_list, tid, SOURCE):
    '''
    Write line format:
    song_id|###|songName|###|artistName|###|typeid|###|SOURCE
    '''
    writeNum = 0
    with open(outfile,'a') as myfile:
        info_list = ["{0}|###|{1}|###|{2}\n".format('|###|'.join(info),tid,SOURCE) for info in songinfo_list]
        myfile.writelines(info_list)
        writeNum = len(info_list)
    return writeNum 

    
def main(outfile=defaultFilePath):

    #clear the outfile context
    open(outfile,'w').close()
    
    for tid in TYPE:
        print warning("Get MusicList of Baidu, Type:{0}-{1}".format(tid,TYPE_MAP[tid]))
        songinfo_list_baidu = list()
        offset = 0
        size = 100
        songinfo_list = getMusicListSong_baidu(tid,offset,size)
        while songinfo_list:
            songinfo_list_baidu.extend(songinfo_list)
            offset = offset + len(songinfo_list)
            songinfo_list = getMusicListSong_baidu(tid,offset,size)
        writeNum = writeToFile(outfile, songinfo_list_baidu, tid, SOURCE)
        print warning("Write {0} songinfo to {1}\n".format(writeNum,outfile))

    print warning("Get MusicList of Baidu Completed!")


if __name__ == '__main__':
    outfile = defaultFilePath
    if len(sys.argv)==1:
        print warning("The Result will write to DefaultFile:{0}".format(defaultFilePath))
    elif len(sys.argv)>1:
        outfile = sys.argv[1].strip()
        print warning("The Result will write to File:{0}".format(outfile))

    main(outfile)
    
