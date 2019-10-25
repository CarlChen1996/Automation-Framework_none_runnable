# -*- coding: utf-8 -*-
# @Time   : 2019/7/15 10:32
# @Author  : balance.cheng
# @Email   : balance.cheng@hp.com
# @File    : QTPutils.py
# @Project : demo
import time


class HPDMOperator:
    def deploy_task(self, task, deploy_host):
        time.sleep(100)
        print('deploy '+task.get_name()+' finished')
        return True

    def execute_task(self, host):
        time.sleep(300)
        print('execute on '+host.get_ip()+'finished')
        return True

    def get_result(self, host):
        time.sleep(100)
        print('get result on'+host.get_ip()+'finished')
        return True
