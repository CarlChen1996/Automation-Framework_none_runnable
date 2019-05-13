# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 2:09 PM
# @Author  : Balance
# @Email   : balance.cheng@hp.com
# @File    : Script.py
# @Project : framework


class Script:
    def __init__(self):
        self.name = ''
        self.status = ''

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status

    def get_name(self):
        return self.name
