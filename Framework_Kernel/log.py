# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:22 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : log.py
# @Project : Automation-Framework
import os
import time
class Log:
    def __init__(self, name='', type='', level='info'):
        self.name = name
        self.type = type
        self.level = level

    def log(self, msg):
        print('[{}]-[{}]: {}'.format(self.name, self.level, msg))
        with open(
                os.path.join(os.getcwd(),'Log\\{}.log'.format(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()))),
                'a',
                encoding='utf-8',
        ) as f:
            f.write('[{}]-[{}]: {}'.format(self.name, self.level, msg)+'\n')
