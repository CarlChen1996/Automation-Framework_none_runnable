# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:31 PM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : ExecuteQueue.py
# @Project : Automation-Framework
from Common_Library.Queue import Queue

class ExecuteQueue(Queue):

    def deploy_tast(self, task):
        print('deploy')
    def execute_task(self,task):
        print('execute')
    def check_status(self,task):
        print('check status')
    def collect_result(self,task):
        print('collect result')
