#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
MusicList of QQ:
http://y.qq.com/y/static/toplist/json/top/***/1.js?loginUin=0&hostUin=0&format=jsonp&;inCharset=GB2312&outCharset=utf-8¬ice=0&platform=yqq&jsonpCallback=MusicJsonCallback&needNewCode=0

***值：
7：流行指数
2：内地
1：港台
4：日韩
6：欧美
8：快乐男声

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

SOURCE = 'qq'

TYPE = [7,2,1,4,6,8]

TYPE_MAP = {7:"流行指数",
            2:"内地",
            1:"港台",
            4:"日韩",
            6:"欧美",
            8:"快乐男声"}

defaultFilePath = './MusicList_qq_style1.lst'


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

def getMusicListSong_QQ(typeid):
    musiclist_url = 'http://y.qq.com/y/static/toplist/json/top/{0}/1.js?loginUin=0&hostUin=0&format=jsonp&;inCharset=GB2312&outCharset=utf-8¬ice=0&platform=yqq&jsonpCallback=MusicJsonCallback&needNewCode=0'
    page = getPage(musiclist_url.format(typeid))

    if not page:
        print error("get page error")
        print error(musiclist_url.format(typeid))
        return

    info_start = page.find('MusicJsonCallback(') + len('MusicJsonCallback(')
    info_end = page.rfind(')')
    
    try:
        data = demjson.decode(page[info_start:info_end])
    except Exception as e:
        print error(e)
    
    songinfo_list = list()
    song_list = data.get('l',list())
    if not song_list:
        #print warning('End of Musiclist')
        return

    htmlP = HTMLParser.HTMLParser() #Decode HTML entities
    for song in song_list:
        song_detail = song.get('s','')
        fields = song_detail.split('|')

        if len(fields) == 23:
            song_key = fields[20] # mmid
        else:
            print error("song_key error, check qqmusic api")
            sys.exit(1)
        songId = fields[0]
        songName = htmlP.unescape(fields[1])
        artistName = htmlP.unescape(fields[3])
        if song_key and songId and songName and artistName:
            songinfo_list.append([song_key,songId,songName,artistName])

    return songinfo_list


def writeToFile(outfile, songinfo_list, tid, SOURCE):
    '''
    Write line format:
    song_key|###|song_id|###|songName|###|artistName|###|typeid|###|SOURCE
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
        print warning("Get MusicList of QQ, Type:{0}-{1}".format(tid,TYPE_MAP[tid]))
        songinfo_list = getMusicListSong_QQ(tid)
        writeNum = writeToFile(outfile, songinfo_list, tid, SOURCE)
        print warning("Write {0} songinfo to {1}\n".format(writeNum,outfile))

    print warning("Get MusicList of QQ Completed!")


if __name__ == '__main__':
    outfile = defaultFilePath
    if len(sys.argv)==1:
        print warning("The Result will write to DefaultFile:{0}".format(defaultFilePath))
    elif len(sys.argv)>1:
        outfile = sys.argv[1].strip()
        print warning("The Result will write to File:{0}".format(outfile))

    main(outfile)
    
