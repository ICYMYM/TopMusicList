#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
MusicList of 163:
http://music.163.com/api/playlist/detail/?id=3778678&updateTime=0&MUSIC_A=ff01acc2d5fff3cd39a3f3dcbebce81ccc71df99407569c1cf45ecc8479540731dca691cd5a4b27329a012da83af261a044bb0759dab1eca944d6489de79f0f1

id值
3779629：新歌
3778678：热歌
2884035：原创
60198：美国Billboard周榜
180106：UK排行榜周榜
60131：日本Oricon周榜
60255：韩国Mnet排行榜周榜
120001：Hit FM Top榜
112463：台湾Hito排行榜
112504：中国TOP排行榜（港台榜）
64016：中国TOP排行榜（内地榜）
3812895：Beatport全球电子舞曲榜
256172：Channel[V]华语榜
257105：Channel[V]欧美榜
256189：Channel[V]日韩榜
4395559：华语金曲榜
1899724：中国嘻哈榜
3906086：华语巴士音乐榜

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

SOURCE = '163'

TYPE = [3779629,3778678,2884035,60198,180106,60131,60255,120001,112463,112504,64016,3812895,256172,257105,256189,4395559,1899724,3906086]

TYPE_MAP = {3779629:"新歌",
            3778678:"热歌",
            2884035:"原创",
            60198:"美国Billboard周榜",
            180106:"UK排行榜周榜",
            60131:"日本Oricon周榜",
            60255:"韩国Mnet排行榜周榜",
            120001:"Hit FM Top榜",
            112463:"台湾Hito排行榜",
            112504:"中国TOP排行榜（港台榜）",
            64016:"中国TOP排行榜（内地榜）",
            3812895:"Beatport全球电子舞曲榜",
            256172:"Channel[V]华语榜",
            257105:"Channel[V]欧美榜",
            256189:"Channel[V]日韩榜",
            4395559:"华语金曲榜",
            1899724:"中国嘻哈榜",
            3906086:"华语巴士音乐榜"}


defaultFilePath = './MusicList_163.lst'


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

def getMusicListSong_163(typeid):
    musiclist_url = 'http://music.163.com/api/playlist/detail/?id={0}&updateTime=0&MUSIC_A=ff01acc2d5fff3cd39a3f3dcbebce81ccc71df99407569c1cf45ecc8479540731dca691cd5a4b27329a012da83af261a044bb0759dab1eca944d6489de79f0f1'
    page = getPage(musiclist_url.format(typeid))

    if not page:
        print error("get page error")
        print error(musiclist_url.format(typeid))
        return

    try:
        data = demjson.decode(page)
    except Exception as e:
        print error(e)
    
    songinfo_list = list()
    song_list = data.get('result',list()).get('tracks',list())
    if not song_list:
        return

    htmlP = HTMLParser.HTMLParser() #Decode HTML entities
    for song in song_list:
        songId = song.get('id')
        songName = htmlP.unescape(song.get('name'))
        artistName = list()
        artists = htmlP.unescape(song.get('artists',list()))
        for ar in artists:
            arn = ar.get('name','')
            if arn:
                artistName.append(arn)
        if songId and songName and artistName:
            songinfo_list.append([str(songId), songName, ','.join(artistName)])

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
        print warning("Get MusicList of 163, Type:{0}-{1}".format(tid,TYPE_MAP[tid]))
        songinfo_list = getMusicListSong_163(tid)
        writeNum = writeToFile(outfile, songinfo_list, tid, SOURCE)
        print warning("Write {0} songinfo to {1}\n".format(writeNum,outfile))

    print warning("Get MusicList of 163 Completed!")


if __name__ == '__main__':
    outfile = defaultFilePath
    if len(sys.argv)==1:
        print warning("The Result will write to DefaultFile:{0}".format(defaultFilePath))
    elif len(sys.argv)>1:
        outfile = sys.argv[1].strip()
        print warning("The Result will write to File:{0}".format(outfile))

    main(outfile)
    
