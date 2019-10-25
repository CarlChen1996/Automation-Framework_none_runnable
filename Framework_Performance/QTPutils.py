# -*- coding: utf-8 -*-
# @Time   : 2019/7/15 10:32
# @Author  : balance.cheng
# @Email   : balance.cheng@hp.com
# @File    : QTPutils.py
# @Project : demo
import time


class HPDMOperator:
    def deploy_task(self, task, deploy_host):
        print('deploy '+task.get_name()+' finished')
        time.sleep(100)
        return True

    def execute_task(self, host):
        print('execute on '+host.get_ip()+'finished')
        time.sleep(300)
        return True

    def get_result(self, host):
        print('get result on'+host.get_ip()+'finished')
        time.sleep(100)
        return True
