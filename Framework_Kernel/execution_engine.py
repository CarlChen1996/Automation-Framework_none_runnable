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
from Framework_Kernel.task_queue import Queue
from Framework_Kernel.analyzer import Analyzer
from Framework_Kernel.validator import HostValidator
from Framework_Kernel.report import Report
from Framework_Kernel.log import execution_log


class ExecutionEngine(Engine):
    def __init__(self, deploy_list, pipe):
        self.__pipe = pipe
        self.__deploy_list = deploy_list
        self.execution_queue = Queue()
        self.__max_thread_count = 5
        self.__current_thread_count = 0
        self.__temp_task_list = []
        self.__temp_host_list = []
        self.__fresh_temp_list_interval = self.__load_config()
        # self.execution_queue.task_list=[]
        # -----------execute结束后需要同时删除task list-----------------
        # execution_queue.task_list = task_list.copy()

    def __load_config(self):
        analyer = Analyzer()
        settings_dict = analyer.analyze_file(os.path.join(os.getcwd(), r'Configuration\config_framework_list.yml'))
        # -----------FTP settings ----------------
        fresh_temp_list_interval = settings_dict['global_settings']['LOOP_INTERVAL']
        return fresh_temp_list_interval

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
        thread_executor = threading.Thread(target=self.__multi_execute, args=())
        thread_executor.setDaemon(True)
        thread_executor.start()
        thread_executor.join()

    def __add_task_to_queue(self):
        while 1:
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
        time.sleep(1)  # can be removed

    def __execute(self, task, host):
        try:
            self.deploy(host, task)
            task.end_time = datetime.datetime.now()
            self.download_result()
            self.send_report(task)
            execution_log.info('[thread_executor] task left in execute queue: {}'.format(
                len(self.execution_queue.get_task_list())))
            time.sleep(1)  # can be removed
            execution_log.info('[thread_executor] task_list now is : {}'.
                               format(list(map(lambda i: i.get_name(), self.execution_queue.get_task_list()))))
            self.__current_thread_count -= 1
            task.set_state('Execute Finished')
            host.state = 'Idle'
        except Exception as e:
            execution_log.info('Unexpect error happen, roll back the task state and host state. Details reason:\n {}'.format(e))
            self.__current_thread_count -= 1
            task.set_state('Assemble Finished')
            host.state = 'Idle'

    def __multi_execute(self):
        while 1:
            print('=======================================================')
            print('==========Begin to Start New Execute Thread==============')
            print('=======================================================')
            execution_log.info('[thread_executor] task_list left: {}'.format(len(self.__temp_task_list)))
            if not self.__temp_task_list:
                self.__fresh_temp_task_list()
            execute_task = self.__temp_task_list[0]
            self.__temp_task_list.remove(execute_task)
            if not self.__temp_host_list:
                self.__fresh_temp_host_list()
            deploy_host = self.__temp_host_list[0]
            self.__temp_host_list.remove(deploy_host)
            while 1:
                # loop when thread queue is full
                try:
                    if self.__current_thread_count > self.__max_thread_count:
                        execution_log.info(
                            'current thread queue is full, waiting task finished')
                        time.sleep(self.__fresh_temp_list_interval)
                    else:
                        execute_task.set_state('Executing')
                        deploy_host.state = 'Busy'
                        self.__current_thread_count += 1
                        new_thread = threading.Thread(target=self.__execute, args=(execute_task, deploy_host))
                        new_thread.setDaemon(True)
                        new_thread.start()
                        new_thread.join(2)
                        break
                except Exception as e:
                    execution_log.error('New thread Error, Exception:\n{}'.format(e))
                    self.__current_thread_count -= 1
                    deploy_host.state = 'Idle'
                    execute_task.set_state('Assemble Finished')

    @staticmethod
    def deploy(deploy_server_host, task):
        # deploy task -> execute task -> collect result
        execution_log.info(
            'execute_engine deploy {} to {} with {}'.format(task.get_name(), task.get_uut_list()[0].get_hostname(),
                                                            deploy_server_host.get_hostname()))
        task.deploy(deploy_server_host)
        execution_log.info('execute_engine execute {}'.format(task.get_name()))
        task.execute(deploy_server_host)
        execution_log.info('execute_engine collect result {}'.format(task.get_name()))
        task.collect_result(deploy_server_host)

    def __fresh_temp_task_list(self):
        while 1:
            execution_log.info('=======================Begin to fresh temp task list==========================')
            for _task in self.execution_queue.get_task_list():
                if _task.get_state() == 'Assemble Finished':
                    self.__temp_task_list.append(_task)
            if not self.__temp_task_list:
                execution_log.info('---No valid task, waiting for new task-----')
                time.sleep(self.__fresh_temp_list_interval)
            else:
                return

    def __fresh_temp_host_list(self):
        while 1:
            execution_log.info('=======================Begin to fresh temp host list==========================')
            for _host in self.__deploy_list:
                print('========', _host.status)
                if _host.state.upper() == 'IDLE':
                    self.__temp_host_list.append(_host)
            if not self.__temp_host_list:
                execution_log.info('---No valid Deploy host, waiting for new host-----')
                time.sleep(self.__fresh_temp_list_interval)
            else:
                return

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

    def send_report(self, task):
        report = Report(task)
        # Send Email
        email_subject, email_to, html, att_zip, task_report_path = self.email_parameter(report, task)
        if html is not False:
            email_handler = Email()
            email_handler.send_email(email_subject, email_to, html.encode('utf-8'), 'html', attachment=att_zip)
            email_handler.disconnect()
            report.remove_report_folder(task_report_path)
            os.remove(att_zip)
            self.execution_queue.remove_task(task)
            execution_log.info("[thread_executor] remove {} from task_list".format(task.get_name()))
            execution_log.info('[thread_executor] remove {} from execute queue'.format(task.get_name()))
        else:
            execution_log.info("Failed to find the email template, please double check")

    @staticmethod
    def email_parameter(report, task):
        task_report_path = report.generate()
        email_to = task.get_email()
        email_subject = 'Thin Client QA Automation Test Report'
        email_vars = {
            'status': 'Normal',
            'project_name': task.get_name(),
            'framework_version': '1.0',
            'script_version': '1.0',
            'start': task.start_time,
            'end': task.end_time,
            'pass_rate': report.total['Passing rate'] + '%',
            'planned': report.total['Count'],
            'passed': report.total['Pass'],
            'failed': report.total['Fail']
        }
        # Zip Attachment
        # att_file = os.path.basename(os.path.normpath(task_report_path)) + '.zip'
        result_path = task_report_path + '.zip'
        att_zip = zip_dir(task_report_path, result_path)
        # Render Email
        analyze_handler = Analyzer()
        setting_file = r'.\Configuration\config_framework_list.yml'
        settings = analyze_handler.analyze_file(setting_file)
        template_file = settings['email_settings']['report_summary']
        html = render_template(template_file, vars=email_vars)
        return email_subject, email_to, html, att_zip, task_report_path
