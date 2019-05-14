# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:38
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : Analyzer.py
# @Project : demo
import sys
from Framework_Kernel.log import Log


log = Log('analyzer')


class Analyzer:
    def __init__(self, file_list=None):
        self.file_list = file_list

    def load(self):
        log.log('Load Data from file ')
        return 'Load data'

    def generate(self):
        log.log('generate Data')
        return 'generate data'
