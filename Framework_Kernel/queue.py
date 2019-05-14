# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 2:06 PM
# @Author  : Balance
# @Email   : balance.cheng@hp.com
# @File    : Queue.py
# @Project : framework


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
        self.task_list = []

    def build_task(self, task, host):
        task.build(host)


class ExecuteQueue(Queue):
    def __init__(self):
        self.task_list = []

    def deploy(self, task, host):
        task.deploy(host)
        print('Q deploy task')

    def execute(self, task):
        for host in task.get_uut_list():
            task.execute(host)
            print('Q execute task finished')

    def check_status(self, task):
        for host in task.get_uut_list():
            task.check_status(host)
        print('Q check status')

    def collect_result(self, task):
        for host in task.get_uut_list():
            task.collect_result(host)
        print('Q collect result')
