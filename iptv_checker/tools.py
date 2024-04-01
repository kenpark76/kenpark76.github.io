#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import urllib.error
import time
import os
import socket

socket.setdefaulttimeout(5.0)

class Tools (object) :

    def __init__ (self) :
        pass

    def chkPlayable (self, url) :
        try:
            startTime = int(round(time.time() * 1000))
            code = urllib.request.urlopen(url).getcode()
            if code == 200 :
                endTime = int(round(time.time() * 1000))
                useTime = endTime - startTime
                return int(useTime)
            else:
                return 0
        except:
            return 0

    def logger (self, txt, new = False) :
        filePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log.txt')
        if new :
            typ = 'w'
        else :
            typ = 'a'
        with open(filePath, typ) as f: 
            f.write(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()) + ": " + txt + "\r\n")
