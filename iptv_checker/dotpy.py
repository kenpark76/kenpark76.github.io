#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tools
import time
import os
import urllib
import m3u8
from threads import ThreadPool

class Source (object) :
    playlist_file = 'playlists/'
    m3u8_file_path = 'output/'
    delay_threshold = 5000

    
    def __init__ (self):
        self.T = tools.Tools()
        self.now = int(time.time() * 1000)
        
    def getSource(self):
        
        '''
        :return playList:
        #从playlist文件夹读取文件，反馈urlList。
        #目前支持两类格式:
        #1、m3u文件格式
        #2、.txt格式，但内容必须是如下格式：
        战旗柯南1,http://dlhls.cdn.zhanqi.tv/zqlive/69410_SgVxl.m3u8
        战旗柯南2,http://alhls.cdn.zhanqi.tv/zqlive/219628_O3y9l.m3u8
        '''
        #playList=[]
        #读取文件
        path = os.listdir(self.playlist_file)
        indexCount = 0
        for p in path:
            
            if os.path.isfile(self.playlist_file + p):
                if p[-4:]=='.txt':
                    with open(self.playlist_file + p,'r',encoding='utf-8') as f:
                        lines = f.readlines()
                        total = len(lines)
                        threads = ThreadPool(1)
                        for i in range(0, total):
                            line = lines[i].strip('\n')
                            item = line.split(',', 1)
                            if len(item)==2:
                                #data = {
                                #    'title': item[0],
                                #    'url': item[1],
                                #}
                                threads.add_task(self.detectData, title = item[0], url = item[1], index=indexCount)
                                #playList.append(data)
                elif p[-5:]=='.m3u8':

                    try:
                        m3u8_obj = m3u8.load(self.playlist_file + p)
                        total = len(m3u8_obj.segments)
                        threads = ThreadPool(20)
                        for i in range(0, total):
                            tmp_title = m3u8_obj.segments[i].title
                            tmp_url = m3u8_obj.segments[i].uri
                            #data={
                            #    'title': tmp_title,
                            #    'url': tmp_url,
                            #}
                            threads.add_task(self.detectData, title = tmp_title, url = tmp_url, index=i)
                            #playList.append(data)
                    except Exception as e:
                        print(e)
            indexCount = indexCount + 1
        #return playList
        
    def getSource111 (self) :
        
        #gitURL = 'https://kenpark76.github.io/koreatv.txt'
        gitURL = 'https://epg.pw/test_channels.txt'
        print("Download Start, URL: ", gitURL)
        urllib.request.urlretrieve(gitURL, "dotpy_source")
        print("Download End, URL: ", gitURL)
        sourcePath = './dotpy_source'
        
        
        with open(sourcePath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            total = len(lines)
            threads = ThreadPool(1)

            for i in range(0, total):
                line = lines[i].strip('\n')
                item = line.split(',', 1)
                if len(item) == 2 :
                    threads.add_task(self.detectData, title = item[0], url = item[1], index=i)
                else :
                    pass
                    
            threads.wait_completion()
        
    def detectData (self, title, url, index) :
        #print('detectData', title, url)
        if index == 0 :
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tvlist.txt'), 'w', encoding='utf-8') as fff:
                fff.write("")
        if url == "#genre#" :
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tvlist.txt'), 'a', encoding='utf-8') as fff:
                fff.write("%s,%s\n" % (title, url))
                
        netstat = self.T.chkPlayable(url)

        if netstat > 0 :
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tvlist.txt'), 'a', encoding='utf-8') as fff:
                fff.write("%s,%s\n" % (title, url))
            print('writeData: ', title, url, netstat)
            self.T.logger('writeData: %s, %s, %s' % (title, url, netstat))
        else :
            print('skipData: ', title, url, netstat)
            self.T.logger('skipData: %s, %s, %s' % (title, url, netstat))
