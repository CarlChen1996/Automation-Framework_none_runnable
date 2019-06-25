# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:22 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : log.py
# @Project : Automation-Framework
import os
import time
import datetime


class Log:
    def __init__(self, name='', type='', level='info'):
        self.__name = name
        self.__type = type
        self.__level = level

    def log(self, msg):
        self.log_path = os.path.join(
            os.getcwd(),
            'Log\\{}\\'.format(time.strftime("%Y-%m-%d_%H", time.localtime())))
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)
        print('[{}]-[{}]-[{}]: {}'.format(
            datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f"),
            self.__name, self.__level, msg))
        with open(
                self.log_path + '{}.log'.format(self.__name),
                'a',
                encoding='utf-8',
        ) as f:
            f.write('[{}]-[{}]-[{}]: {}'.format(
                datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f"),
                self.__name, self.__level, msg) + '\n')
