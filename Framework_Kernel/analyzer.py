# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:38
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : Analyzer.py
# @Project : demo
import sys


class Analyzer:
    def __init__(self, file_list=None):
        self.file_list = file_list

    def load(self):
        print(sys._getframe().f_code.co_name + "  finished")

    def generate(self):
        print(sys._getframe().f_code.co_name + "  finished")
