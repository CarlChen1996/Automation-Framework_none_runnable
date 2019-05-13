# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 10:46 AM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : ExecutionEngine.py
# @Project : Automation-Framework
class ExecutionEngine:
    def __init__(self,status='off'):
        self.status=status
    def start(self):
        print('start')
    def stop(self):
        print('stop')

def execute():
    pass