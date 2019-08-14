# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 2:06 PM
# @Author  : Balance
# @Email   : balance.cheng@hp.com
# @File    : Queue.py
# @Project : framework
from Framework_Kernel.log import assemble_log, execution_log


class Queue:
    def __init__(self):
        self.__task_list = []

    def insert_task(self, index=0, task=''):
        if index == 0:
            self.__task_list.append(task)
        else:
            self.__task_list.insert(index, task)

    def remove_task(self, task):
        self.__task_list.remove(task)

    def set_order(self, index, task):
        pass

    def clear(self):
        self.__task_list = []

    def get_task_list(self):
        return self.__task_list


class AssembleQueue(Queue):
    def __init__(self):
        Queue.__init__(self)
        self.log = assemble_log

    def assemble(self, task, host):
        self.log.info('assemble_queue build {} on {}'.format(
            task.get_name(), host.get_hostname()))
        print("**************************************************")
        print("**************************************************")
        print("**************************************************")
        print("**************************************************")
        print("**************************************************")
        task.build(host)


class ExecuteQueue(Queue):
    def __init__(self):
        Queue.__init__(self)
        self.log = execution_log

    def deploy(self, task, host):
        # host is Deploy Host
        self.log.info('execute_queue deploy {} to {} with {}'.format(
            task.get_name(), task.get_uut_list()[0].get_hostname(), host.get_hostname()))
        task.deploy(host)

    def execute(self, task):
        # host is UUT host
        # for host in task.get_uut_list():
        #     self.log.info('execute_queue execute {} on {}'.format(
        #         task.get_name(), host.get_hostname()))
        #     task.execute(host)
        self.log.info('execute_queue execute {}'.format(task.get_name()))
        task.execute()

    def check_status(self, task):
        for host in task.get_uut_list():
            self.log.info('execute_queue check status {} on {}'.format(
                task.get_name(), host.get_hostname()))
            task.check_status(host)

    def collect_result(self, task):
        # for host in task.get_uut_list():
        #     self.log.info('execute_queue collect result {} from {}'.format(
        #         task.get_name(), host.get_hostname()))
        #     task.collect_result()
        task.collect_result()
        self.log.info('execute_queue collect result {}'.format(task.get_name()))
