# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:32
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : Configurator.py
# @Project : demo
import sys
class Configurator:
    def __init__(self,object_list=None):
        self.object_list=object_list
        pass
    def config(self):
        print(sys._getframe().f_code.co_name + "  finished")

