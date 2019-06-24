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
        self.__pipe = pipe
        self.__deploy_list = deploy_list
        self.__execution_queue = ExecuteQueue()
        self.__executor = Process(target=self.launch, name='framework_executor', args=())

        # self.execution_queue.task_list=[]
        # -----------execute结束后需要同时删除task list-----------------
        # execution_queue.task_list = task_list.copy()

    def start(self):
        self.status = self.__executor
        self.__executor.daemon = True
        self.__executor.start()

    def stop(self):
        self.__executor.terminate()

    def launch(self):
        thread_queue_monitor = threading.Thread(target=self.__add_task_to_queue, args=())
        thread_queue_monitor.setDaemon(True)
        thread_queue_monitor.start()
        thread_executor = threading.Thread(target=self.__execute, args=())
        thread_executor.setDaemon(True)
        thread_executor.start()
        thread_executor.join()

    def __add_task_to_queue(self):
        while not False:
            receive = self.__pipe.recv()
            print('[Execution] received: {}'.format(receive.get_name()))
            self.__pipe.send(receive.get_name())
            log.log("[thread_execution_queue_monitor] receive: {}".format(receive.get_name()))
            self.__execution_queue.insert_task(task=receive)
            log.log('[thread_execution_queue_monitor] append {} to task_list'.format(receive.get_name()))
            log.log('[thread_execution_queue_monitor] task_list now is {}'.
                    format(list(map(lambda i: i.get_name(),self.__execution_queue.get_task_list()))))
            time.sleep(1)

    def __execute(self):
        while True:
            time.sleep(1)
            log.log('[thread_executor] task_list left: {}'.format(len(self.__execution_queue.get_task_list())))
            if self.__execution_queue.get_task_list():
                self.run()
                time.sleep(3)
                log.log('[thread_executor] task_list now is : {}'.
                        format(list(map(lambda i: i.get_name(), self.__execution_queue.get_task_list()))))
            else:
                log.log('[thread_executor]************************ wait for new task to execute **********************')
            time.sleep(5)

    def run(self):
        d = self.__deploy_list[0]
        i = self.__execution_queue.get_task_list()[0]
        # ----------循环里面添加 刷新list的方法 ---------------------
        self.__execution_queue.deploy(i, d)
        self.__execution_queue.execute(i)
        # --------需要得到返回值 ------------------
        self.__execution_queue.check_status(i)
        self.__execution_queue.collect_result(i)
        r = Report(i.get_name(), i.get_uut_list())
        r.generate()
        self.__execution_queue.remove_task(i)
        log.log("[thread_executor] remove {} from task_list".format(i.get_name()))
        log.log('[thread_executor] remove {} from execute queue'.format(i.get_name()))
        log.log('[thread_executor] task left in execute queue: {}'.format(len(self.__execution_queue.get_task_list())))
        print('---------------------------------------------------------------')
