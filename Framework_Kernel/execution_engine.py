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

log = Log('execution')


class ExecutionEngine(Engine):

    def __init__(self, deploy_list, pipe):
        self.pipe = pipe
        self.deploy_list = deploy_list
        self.execution_queue = ExecuteQueue()

        # self.execution_queue.task_list=[]
        # -----------execute结束后需要同时删除task list-----------------
        # execution_queue.task_list = task_list.copy()

    def start(self):
        self.executor = Process(target=self.launch, name='framework_executor', args=())
        self.status = self.executor
        self.executor.daemon = True
        self.executor.start()

    def stop(self):
        self.executor.terminate()

    def launch(self):
        thread_list = []
        thread_queue_monitor = threading.Thread(target=self.add_task_to_queue, args=())
        thread_list.append(thread_queue_monitor)
        thread_executor = threading.Thread(target=self.execute, args=())
        thread_list.append(thread_executor)
        for thread in thread_list:
            thread.setDaemon(True)
            thread.start()
            # t.join()
        thread.join()

    def add_task_to_queue(self):
        while not False:
            receive = self.pipe.recv()
            log.log("[thread_queue_monitor] receive: {}".format(receive.get_name()))
            self.execution_queue.task_list.append(receive)
            log.log('[thread_queue_monitor] append {} to task_list'.format(receive.get_name()))
            log.log('[thread_queue_monitor] task_list now is {}'.format(list(map(lambda i: i.get_name(), self.execution_queue.task_list))))
            time.sleep(1)

    def execute(self):
        while True:
            time.sleep(1)
            log.log('[thread_executor] task_list left: {}'.format(len(self.execution_queue.task_list)))
            if self.execution_queue.task_list:
                self.run()
                time.sleep(3)
                log.log('[thread_executor] task_list now is : {}'.format(list(map(lambda i: i.get_name(), self.execution_queue.task_list))))
            else:
                log.log('[thread_executor]************************ wait for new task to execute **********************')
            time.sleep(5)

    def run(self,):
        d = self.deploy_list[0]
        i = self.execution_queue.task_list[0]
        # ----------循环里面添加 刷新list的方法 ---------------------
        self.execution_queue.deploy(i, d)
        self.execution_queue.execute(i)
        # --------需要得到返回值 ------------------
        self.execution_queue.check_status(i)
        self.execution_queue.collect_result(i)
        r = Report(i.get_name(), i.get_script_list())
        r.generate()
        self.execution_queue.task_list.remove(i)
        log.log("[thread_executor] remove {} from task_list".format(i.get_name()))
        log.log('[thread_executor] remove {} from execute queue'.format(i.get_name()))
        log.log('[thread_executor] task left in execute queue: {}'.format(len(self.execution_queue.task_list)))
        print('---------------------------------------------------------------')


if __name__ == '__main__':
    pass
