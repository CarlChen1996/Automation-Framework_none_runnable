# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 10:46 AM
# @Author  : Carl
# @Email   : carl.chen@hp.com
# @File    : ExecutionEngine.py
# @Project : Automation-Framework
import os
from multiprocessing import Process
import threading
import time
from Framework_Kernel.engine import Engine
from Framework_Kernel.ftp_tools import FTPUtils
from Framework_Kernel.queue_task import ExecuteQueue
'''
from Framework_Kernel.task import Task
from Framework_Kernel.host import WindowsDeployHost, WindowsExecuteHost
'''
from Framework_Kernel.report import Report,Email
from Framework_Kernel.log import execution_log


class ExecutionEngine(Engine):

    def __init__(self, deploy_list, pipe):
        self.__pipe = pipe
        self.__deploy_list = deploy_list
        self.__execution_queue = ExecuteQueue()
        # self.execution_queue.task_list=[]
        # -----------execute结束后需要同时删除task list-----------------
        # execution_queue.task_list = task_list.copy()

    def start(self):
        self.__executor = Process(target=self.start_thread, name='framework_executor', args=())
        self.status = self.__executor
        self.__executor.daemon = True
        self.__executor.start()

    def stop(self):
        self.__executor.terminate()

    def start_thread(self):
        thread_queue_monitor = threading.Thread(target=self.__add_task_to_queue, args=())
        thread_queue_monitor.setDaemon(True)
        thread_queue_monitor.start()
        thread_executor = threading.Thread(target=self.__execute, args=())
        thread_executor.setDaemon(True)
        thread_executor.start()
        thread_executor.join()

    def __add_task_to_queue(self):
        while True:
            receive = self.__pipe.recv()
            execution_log.info('[Execution] received: {}'.format(receive.get_name()))
            self.__pipe.send(receive.get_name())
            execution_log.info("[thread_execution_queue_monitor] receive: {}".format(receive.get_name()))
            self.__execution_queue.insert_task(task=receive)
            execution_log.info('[thread_execution_queue_monitor] append {} to task_list'.format(receive.get_name()))
            execution_log.info('[thread_execution_queue_monitor] task_list now is {}'.
                    format(list(map(lambda i: i.get_name(),self.__execution_queue.get_task_list()))))
            time.sleep(1)

    def __execute(self):
        while True:
            time.sleep(1)
            execution_log.info('[thread_executor] task_list left: {}'.format(len(self.__execution_queue.get_task_list())))
            if self.__execution_queue.get_task_list():
                self.__deploy()
                time.sleep(3)
                execution_log.info('[thread_executor] task_list now is : {}'.
                        format(list(map(lambda i: i.get_name(), self.__execution_queue.get_task_list()))))
            else:
                execution_log.info('[thread_executor]************************ wait for new task to execute **********************')
            time.sleep(5)

    def __deploy(self):
        d = self.__deploy_list[0]
        i = self.__execution_queue.get_task_list()[0]
        # ----------循环里面添加 刷新list的方法 ---------------------
        self.__execution_queue.deploy(i, d)
        self.__execution_queue.execute(i)
        # --------需要得到返回值 ------------------
        # self.__execution_queue.check_status(i)
        self.__execution_queue.collect_result(i)

        ftp_util = FTPUtils()
        task_list = ftp_util.get_list()
        for folder in task_list:
            ftp_util.download_dir(os.path.join('.\\Report', folder), folder)
        ftp_util.close()

        r = Report(i.get_name(), i.get_uut_list())
        e = Email(i.get_email())
        e.zip_result_package(r.generate(),i.get_name())
        e.send()
        self.__execution_queue.remove_task(i)
        execution_log.info("[thread_executor] remove {} from task_list".format(i.get_name()))
        execution_log.info('[thread_executor] remove {} from execute queue'.format(i.get_name()))
        execution_log.info('[thread_executor] task left in execute queue: {}'.format(len(self.__execution_queue.get_task_list())))
        print('---------------------------------------------------------------')



