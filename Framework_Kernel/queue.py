# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 2:06 PM
# @Author  : Balance
# @Email   : balance.cheng@hp.com
# @File    : Queue.py
# @Project : framework
from Framework_Kernel.log import Log




class Queue:
    def __init__(self):
        self.task_list = []

    def insert_task(self, index=0, task=''):
        if index == 0:
            self.task_list.append(task)
        else:
            self.task_list.insert(index, task)

    def remove_task(self, task):
        self.task_list.remove(task)

    def set_order(self, index, task):
        pass

    def clear(self):
        self.task_list = []

    def get_task_list(self):
        return self.task_list


class AssembleQueue(Queue):
    def __init__(self):
        self.log = Log('Assemble Queue')
        self.task_list = []

    def build_task(self, task, host):
        self.log.log('Assembly Queue build {} on {}'.format(task.get_name(), host.hostnamme))
        task.build(host)


class ExecuteQueue(Queue):
    def __init__(self):
        self.log = Log("Execute Queue")
        self.task_list = []

    def deploy(self, task, host):
        self.log.log('Execute Queue deploy {} to {}'.format(task.get_name(), host.hostnamme))
        task.deploy(host)

    def execute(self, task):
        for host in task.get_uut_list():
            self.log.log('Execute Queue execute {} on {}'.format(task.get_name(), host.hostnamme))
            task.execute(host)

    def check_status(self, task):
        for host in task.get_uut_list():
            self.log.log('Execute Queue check status {} on {}'.format(task.get_name(), host.hostnamme))
            task.check_status(host)

    def collect_result(self, task):
        for host in task.get_uut_list():
            self.log.log('Execute Queue collect result {} from {}'.format(task.get_name(), host.hostnamme))
            task.collect_result(host)
