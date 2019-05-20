# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 10:46 AM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : ExecutionEngine.py
# @Project : Automation-Framework
from multiprocessing import Process
import threading
import time
from Framework_Kernel.engine import Engine
from Framework_Kernel.queue import ExecuteQueue
'''
from Framework_Kernel.task import Task
from Framework_Kernel.host import WindowsDeployHost, WindowsExecuteHost
'''
from Framework_Kernel.report import Report
from Framework_Kernel.log import Log

log = Log('Execution')


class ExecutionEngine(Engine):

    def __init__(self, deploy_list, pipe):
        self.pipe = pipe
        self.deploy_list = deploy_list
        self.exeQ = ExecuteQueue()
        self.executor = Process(target=self.execute_q, name='framework_executor', args=())
        self.status = self.executor
        # self.exeQ.task_list=[]
        # -----------execute结束后需要同时删除task list-----------------
        # exeQ.task_list = task_list.copy()

    def start(self):
        self.executor.start()

    def execute_q(self):
        threads_2 = []
        t3 = threading.Thread(target=self.thread_3, args=())
        threads_2.append(t3)
        t4 = threading.Thread(target=self.thread_4, args=())
        threads_2.append(t4)
        for tt in threads_2:
            tt.setDaemon(True)
            tt.start()
            # t.join()
        tt.join()

    def thread_3(self):
        while not False:
            receive = self.pipe.recv()
            log.log("[thread_3] receive: {}".format(receive.get_name()))
            self.exeQ.task_list.append(receive)
            log.log('[thread_3] append {} to task_list'.format(receive.get_name()))
            log.log('[thread_3] task_list now is {}'.format(list(map(lambda i: i.get_name(), self.exeQ.task_list))))
            time.sleep(1)

    def thread_4(self):
        while True:
            time.sleep(1)
            log.log('[thread_4] task_list left: {}'.format(len(self.exeQ.task_list)))
            if self.exeQ.task_list:
                self.execute()
                time.sleep(3)
                log.log('[thread_4] task_list now is : {}'.format(list(map(lambda i: i.get_name(), self.exeQ.task_list))))
            else:
                log.log('[thread_4]************************ wait for new task to execute **********************')
            time.sleep(5)

    def execute(self,):
        d = self.deploy_list[0]
        i = self.exeQ.task_list[0]
        # ----------循环里面添加 刷新list的方法 ---------------------
        self.exeQ.deploy(i, d)
        self.exeQ.execute(i)
        # --------需要得到返回值 ------------------
        self.exeQ.check_status(i)
        self.exeQ.collect_result(i)
        r = Report(i.get_name(), i.get_script_list())
        r.generate()
        self.exeQ.task_list.remove(i)
        log.log("[thread_4] remove {} from task_list".format(i.get_name()))
        log.log('[thread_4] remove {} from execute queue'.format(i.get_name()))
        log.log('[thread_4] task left in execute queue: {}'.format(len(self.exeQ.task_list)))
        print('---------------------------------------------------------------')


if __name__ == '__main__':
    pass
