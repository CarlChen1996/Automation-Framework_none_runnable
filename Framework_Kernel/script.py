# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 2:09 PM
# @Author  : Balance
# @Email   : balance.cheng@hp.com
# @File    : Script.py
# @Project : framework


class Script:
    def __init__(self, name, status='NoRun'):
        self.__name = name
        self.__status = status

    def get_status(self):
        return self.__status

    def set_status(self, status):
        self.__status = status

    def get_name(self):
        return self.__name
