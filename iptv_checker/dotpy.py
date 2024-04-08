#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tools
import time
import os
import urllib
import re
import m3u8
from m3u8 import protocol
from m3u8.parser import save_segment_custom_value
from threads import ThreadPool

class Source (object) :
    playlist_file = 'playlists/'
    m3u8_file_path = 'output/'
    delay_threshold = 5000
    writeCount = 0
    skipCount = 0
    oldFileName = ""

    
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
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tvlist.txt'), 'w', encoding='utf-8') as fff:
            fff.write("")
        for p in path:
            if os.path.isfile(self.playlist_file + p):
                if p[-4:]=='.txt':
                    with open(self.playlist_file + p,'r',encoding='utf-8') as f:
                        self.T.logger('txt file parsing: %s' % (p))
                        print("txt file parsing: ", p)
                        lines = f.readlines()
                        total = len(lines)
                        threads = ThreadPool(1)
                        for i in range(0, total):
                            line = lines[i].strip('\n')
                            item = line.split(',', 1)
                            if len(item)==2:
                                threads.add_task(self.detectData, title = item[0], url = item[1], filename = p)
                                indexCount = indexCount + 1
                        threads.wait_completion()
                elif p[-5:]=='.m3u8':
                    try:
                        self.T.logger('m3u8 file parsing: %s' % (p))
                        print("m3u8 file parsing: ", p)
                        m3u8_obj = m3u8.load(self.playlist_file + p, custom_tags_parser=self.parse_iptv_attributes)
                        total = len(m3u8_obj.segments)
                        threads = ThreadPool(20)
                        for i in range(0, total):
                            tmp_title = m3u8_obj.segments[i].title
                            tmp_url = m3u8_obj.segments[i].uri
                            #segment_props = m3u8_obj.segments[i].custom_parser_values['extinf_props']
                            threads.add_task(self.detectData, title = tmp_title, url = tmp_url, filename = p)
                            indexCount = indexCount + 1
                            #print("parsed Data: ", tmp_title, segment_props['group-title'], segment_props['tvg-logo'],tmp_url )
                        threads.wait_completion()
                    except Exception as e:
                        print(e)
        print("total:", indexCount, "write:", self.writeCount, "skip:", self.skipCount, "invalid:", (indexCount - self.writeCount - self.skipCount))
        self.T.logger('total: %s, write: %s, skip: %s, invalid: %s' % (indexCount, self.writeCount, self.skipCount, (indexCount - self.writeCount - self.skipCount)))

    '''    
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
    '''
        
    def detectData (self, title, url, filename) :
        #print('detectData', title, url)

        if url == "#genre#" :
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tvlist.txt'), 'a', encoding='utf-8') as fff:
                fff.write("%s,%s\n" % (title, url))
                
        netstat = self.T.chkPlayable(url)

        if netstat > 0 :
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tvlist.txt'), 'a', encoding='utf-8') as fff:
                if self.oldFileName != filename :
                    if filename[-5:] == '.m3u8' :
                        fff.write(filename[:-5] + ",#genre#" + "\n")
                    if filename[-4:] == '.txt' :
                        fff.write(filename[:-4] + ",#genre#" + "\n")
                    self.oldFileName = filename
                fff.write("%s,%s\n" % (title, url))
                self.writeCount = self.writeCount + 1
            print('writeData: ', title, url, netstat)
            self.T.logger('writeData: %s, %s, %s' % (title, url, netstat))
        else :
            self.skipCount = self.skipCount + 1
            print('skipData: ', title, url, netstat)
            self.T.logger('skipData: %s, %s, %s' % (title, url, netstat))
            
            
    def parse_iptv_attributes(self, line, lineno, data, state):
        # Customize parsing #EXTINF
        if line.startswith(protocol.extinf):
            title = ''
            chunks = line.replace(protocol.extinf + ':', '').split(',', 1)
            if len(chunks) == 2:
                duration_and_props, title = chunks
            elif len(chunks) == 1:
                duration_and_props = chunks[0]

            additional_props = {}
            chunks = duration_and_props.strip().split(' ', 1)
            if len(chunks) == 2:
                duration, raw_props = chunks
                matched_props = re.finditer(r'([\w\-]+)="([^"]*)"', raw_props)
                for match in matched_props:
                    additional_props[match.group(1)] = match.group(2)
            else:
                duration = duration_and_props

            if 'segment' not in state:
                state['segment'] = {}
            state['segment']['duration'] = float(duration)
            state['segment']['title'] = title

            # Helper function for saving custom values
            save_segment_custom_value(state, 'extinf_props', additional_props)

            # Tell 'main parser' that we expect an URL on next lines
            state['expect_segment'] = True

            # Tell 'main parser' that it can go to next line, we've parsed current fully.
            return True
            
