# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:32
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : Configurator.py
# @Project : demo
import sys
from Framework_Kernel.log import Log


log = Log('Configurator')


class Configurator:
    def __init__(self, object_list=None):
        self.object_list = object_list
        pass

    def config(self):
        log.log(sys._getframe().f_code.co_name + "  finished")
