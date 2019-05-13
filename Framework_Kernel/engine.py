# -*- coding: utf-8 -*-
# @Time   : 2019/5/13 14:23
# @Author  : Bamboo.pan
# @Email   : Bamboo.pan@hp.com
# @File    : Engine.py
# @Project : demo


class Engine:
    def __init__(self, status='off'):
        self.status = status

    def start(self):
        print('start')

    def stop(self):
        print('stop')
