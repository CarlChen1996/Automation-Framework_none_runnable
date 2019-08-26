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
import datetime
from Framework_Kernel.engine import Engine
from Common_Library.file_transfer import FTPUtils
from Common_Library.email_operator import Email
from Common_Library.functions import render_template, zip_dir
from Framework_Kernel.task_queue import ExecuteQueue
from Framework_Kernel.analyzer import Analyzer
from Framework_Kernel.validator import HostValidator
'''
from Framework_Kernel.task import Task
from Framework_Kernel.host import WindowsDeployHost, WindowsExecuteHost
'''
from Framework_Kernel.report import Report
from Framework_Kernel.log import execution_log


class ExecutionEngine(Engine):

    def __init__(self, deploy_list, pipe):
        self.__pipe = pipe
        self.__deploy_list = deploy_list
        self.execution_queue = ExecuteQueue()
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
            self.insert_task_to_queue()

    def insert_task_to_queue(self):
        receive = self.__pipe.recv()
        execution_log.info('[Execution] received: {}'.format(receive.get_name()))
        self.__pipe.send(receive.get_name())
        execution_log.info("[thread_execution_queue_monitor] receive: {}".format(receive.get_name()))
        self.execution_queue.insert_task(task=receive)
        execution_log.info('[thread_execution_queue_monitor] append {} to task_list'.format(receive.get_name()))
        execution_log.info('[thread_execution_queue_monitor] task_list now is {}'.
                           format(list(map(lambda i: i.get_name(), self.execution_queue.get_task_list()))))
        time.sleep(1)

    def __execute(self):
        while True:
            execution_log.info('[thread_executor] task_list left: {}'.format(len(self.execution_queue.get_task_list())))
            if self.execution_queue.get_task_list():
                d = self.__deploy_list[0]
                i = self.execution_queue.get_task_list()[0]
                self.deploy(d, i)
                i.end_time = datetime.datetime.now()
                self.download_result()
                self.send_report(i)
                execution_log.info('[thread_executor] task left in execute queue: {}'.format(
                    len(self.execution_queue.get_task_list())))
                time.sleep(3)
                print('---------------------------------------------------------------')
                execution_log.info('[thread_executor] task_list now is : {}'.
                                   format(list(map(lambda i: i.get_name(), self.execution_queue.get_task_list()))))
            else:
                execution_log.info(
                    '[thread_executor]************************ wait for new task to execute **********************')
            time.sleep(10)

    def deploy(self, d, i):
        # deploy task -> execute task -> collect result
        execution_log.info(
            'execute_engine deploy {} to {} with {}'.format(i.get_name(), i.get_uut_list()[0].get_hostname(),
                                                            d.get_hostname()))
        i.deploy(d)
        execution_log.info('execute_engine execute {}'.format(i.get_name()))
        i.execute()
        execution_log.info('execute_engine collect result {}'.format(i.get_name()))
        i.collect_result()

    @staticmethod
    def download_result():
        # Retrive FTP Settings from configuration file
        config_file = os.path.join(os.getcwd(), r'.\Configuration\config_framework_list.yml')
        analyze_handler = Analyzer()
        ftp_settings = analyze_handler.analyze_file(config_file)['ftp_settings']
        validate_ftp = HostValidator.validate_ftp(ftp_settings)
        if validate_ftp:
            ftp_util = FTPUtils(ftp_settings['server_address'], ftp_settings['username'], ftp_settings['password'])
            task_list = ftp_util.get_item_list(ftp_settings['result_file_path'])
            for folder in task_list:
                ftp_util.download_dir(folder, os.path.join('.\\Report', folder))
                ftp_util.delete_dir(folder)
            ftp_util.close()

    def send_report(self, i):
        r = Report(i)
        # Send Email
        email_subject, email_to, html, att_zip, task_report_path = self.email_parameter(r, i)
        if html is not False:
            email_handler = Email()
            email_handler.send_email(email_subject, email_to, html.encode('utf-8'), 'html', attachment=att_zip)
            email_handler.disconnect()
            r.remove_report_folder(task_report_path)
            self.execution_queue.remove_task(i)
            execution_log.info("[thread_executor] remove {} from task_list".format(i.get_name()))
            execution_log.info('[thread_executor] remove {} from execute queue'.format(i.get_name()))
        else:
            execution_log.info("Failed to find the email template, please double check")

    @staticmethod
    def email_parameter(r, i):
        task_report_path = r.generate()
        email_to = i.get_email()
        email_subject = 'Thin Client QA Automation Test Report'
        email_vars = {
            'status': 'Normal',
            'project_name': i.get_name(),
            'framework_version': '1.0',
            'script_version': '1.0',
            'start': i.start_time,
            'end': i.end_time,
            'pass_rate': r.total['Passing rate'] + '%',
            'planned': r.total['Count'],
            'passed': r.total['Pass'],
            'failed': r.total['Fail']
        }
        # Zip Attachment
        att_file = os.path.basename(os.path.normpath(task_report_path)) + '.zip'
        result_path = os.path.join(task_report_path, att_file)
        att_zip = zip_dir(task_report_path, result_path)
        # Render Email
        analyze_handler = Analyzer()
        setting_file = r'.\Configuration\config_framework_list.yml'
        settings = analyze_handler.analyze_file(setting_file)
        template_file = settings['email_settings']['report_summary']
        html = render_template(template_file, vars=email_vars)
        return email_subject, email_to, html, att_zip, task_report_path
