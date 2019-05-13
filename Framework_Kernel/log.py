# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:22 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : log.py
# @Project : Automation-Framework


class Log:
    def __init__(self, name='', type='', level=''):
        self.name = name
        self.type = type
        self.level = level

    def log(self, level, msg):
        self.level = level
        print(self.name + '-' + self.level + '-' + msg)
        with open(
                'log.log',
                'w',
                encoding='utf-8',
        ) as f:
            f.write(self.name + '-' + self.level + '-' + msg)
