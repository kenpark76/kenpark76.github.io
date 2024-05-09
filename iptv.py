#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tools
import dotpy

class Iptv (object):

    def __init__ (self) :
        self.T = tools.Tools()

    def run(self) :
        self.T.logger("Log Start", True)

        Dotpy = dotpy.Source()
        Dotpy.getSource()


        self.T.logger("Log End")

if __name__ == '__main__':
    obj = Iptv()
    obj.run()
