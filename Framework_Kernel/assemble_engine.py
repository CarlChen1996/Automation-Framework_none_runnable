# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:27 PM
# @Author  : balance
# @Email   : balance.cheng@hp.com
# @File    : AssembleEngine.py
# @Project : Automation-Framework
from Framework_Kernel.engine import Engine
from Framework_Kernel.task_queue import Queue
from Framework_Kernel.analyzer import Analyzer
from Framework_Kernel.task import Task
from Framework_Kernel.host import WindowsExecuteHost, LinuxExecuteHost, WindowsBuildHost, LinuxBuildHost
from Framework_Kernel.validator import HostValidator
from Framework_Kernel.validator import ScriptValidator
from Framework_Kernel.script import Script
from Framework_Kernel.log import assemble_log
from Framework_Kernel.error_handler import ErrorMsg, ErrorLevel, ErrorHandler, EngineCode
from multiprocessing import Process
import time
import threading
import os
import datetime


class AssembleEngine(Engine):
    def __init__(self, pipe, build_list):
        self.__pipe = pipe
        self.__build_node_list = build_list
        self.assembleQueue = Queue()
        self.global_settings = self.__load_config()
        self.loop_interval = self.global_settings['loop_interval']
        self.max_thread_count_win = self.global_settings['max_build_thread_win']
        self.max_thread_count_linux = self.global_settings['max_build_thread_linux']
        self.current_thread_count_win = 0
        self.current_thread_count_linux = 0
        self.tasklist = []
        self.test_plan_folder = os.path.join(os.getcwd(), 'Test_Plan')
        self.temp_task_win = []
        self.temp_node_win = []
        self.temp_task_linux = []
        self.temp_node_linux = []

    def __load_config(self):
        analyer = Analyzer()
        settings_dict = analyer.analyze_file(os.path.join(os.getcwd(), r'Configuration\config_framework_list.yml'))
        global_settings = settings_dict['global_settings']
        return global_settings

    def start(self):
        self.__assembler = Process(target=self.start_thread,
                                   name='framework_Assembler',
                                   args=())
        self.__assembler.daemon = True
        self.status = self.__assembler
        self.__assembler.start()

    def stop(self):
        self.__assembler.terminate()

    def start_thread(self):
        refresh_queue_thread = threading.Thread(target=self.__fresh_queue_testplan,
                                                name='fresh_queue_testplan',
                                                args=())
        refresh_queue_thread.setDaemon(True)
        refresh_queue_thread.start()
        refresh_queue_execute = threading.Thread(
            target=self.__fresh_queue_execution)
        refresh_queue_execute.setDaemon(True)
        refresh_queue_execute.start()
        assembler_thread = threading.Thread(target=self.__assemble,
                                            name='thread_assemble_task',
                                            args=())
        assembler_thread.setDaemon(True)
        assembler_thread.start()
        assembler_thread.join()

    def __fresh_queue_testplan(self):
        """
        refresh Queue from test plan in test folder
        :return: None
        """
        while True:
            file_list = self.scan_folder()
            self.get_task_from_folder(file_list)

    def scan_folder(self):
        assemble_log.info(
            '[Thread_fresh_testplan] ***************begin to refresh queue *****************'
        )
        temp_list = os.listdir(self.test_plan_folder)
        file_list = []
        for i in temp_list:
            if i[:10] == 'TEST_PLAN_':
                file_list.append(os.path.join(self.test_plan_folder, i))
        return file_list

    def get_task_from_folder(self, file_list):
        if len(file_list) == 0:
            time.sleep(10)
        else:
            self.generate_task(file_list)

    def generate_task(self, file_list):
        analyzer = Analyzer()
        task_data = analyzer.analyze_files_in_list(file_list)
        # ********* put filepath into taskitem dict: key:file_path, value: file path
        task_source_list = []
        for i in task_data:
            file_path = list(i.keys())[0]
            i[file_path]['file_path'] = file_path
            task_source_list.append(i[file_path])
        """
        # task_data: [{filepath1:taskitem1},{filepath2:taskitem2}]
        # task_source_list: [taskitem1, taskitem2]
        # taskitem: {               name:task1,
        #                           testscripts:[script1, script2,],
        #                           uutlist:[uutinformatio,uutinformation],
        #                           needbuild:True
                                    email:xxx.xxx@hp.com
                                    repository:https://hp.com
        #                           file_path:c:\\xxxx\\xxx\\testplan\\xxx.xlsx}
        # uutinformation: {         ip:1.1.1.1,
        #                           mac:1234566,
        #                           os: win7e}}
        # ************************************************************************
        """
        for taskitem in task_source_list:
            task = Task(taskitem['name'], taskitem['email'],
                        taskitem['repository'], taskitem['needbuild'])
            task.start_time = datetime.datetime.now()
            task.set_state('Wait Assemble')
            for script in taskitem['testscripts']:
                task.insert_script(Script(name=script))
            for uutitem in taskitem['uutlist']:
                """
                generate UUT instance according os of uut，if str(os)
                contains Win or WES(support by tester), use windowhost, else use linux host
                """
                if 'WIN' in uutitem['os'].upper() or 'WES' in uutitem['os'].upper():
                    uut = WindowsExecuteHost(ip=uutitem['ip'],
                                             version=uutitem['os'],
                                             mac=uutitem['mac'])
                    task.insert_uut_list(uut)
                else:
                    uut = LinuxExecuteHost(ip=uutitem['ip'], version=uutitem['os'], mac=uutitem['mac'])
                    task.insert_uut_list(uut)
            assemble_log.info(
                '[Thread_fresh_testplan]--insert {} to assemble queue list'.format(task.get_name()))

            if self.validate_task(task):
                self.assembleQueue.insert_task(task=task)

            # -------------------rename task plan name -------------------------
            os.rename(
                taskitem['file_path'],
                taskitem['file_path'][:taskitem['file_path'].index('TEST_PLAN')] + 'Loaded_' + taskitem['file_path']
                [taskitem['file_path'].index('TEST_PLAN'):])
            assemble_log.info(
                'rename finished' + taskitem['file_path'][:taskitem['file_path'].index('TEST_PLAN')] + 'Loaded_' + taskitem['file_path']
                [taskitem['file_path'].index('TEST_PLAN'):])
        assemble_log.info(
            '[Thread_fresh_testplan] ***************finish refresh queue *****************'
        )
        assemble_log.info(
            '[Thread_fresh_testplan] left task in assemble queue: {}'.format(
                len(self.assembleQueue.get_task_list())))
        time.sleep(10)

    def __fresh_queue_execution(self):
        while True:
            assemble_log.info(
                '[fresh_queue_execution]-------begin to refresh----fresh_queue_execution----------------'
            )
            assemble_log.info('task_list left:{}'.format(
                len(self.assembleQueue.get_task_list())))
            self.send_task_to_execution()

    def send_task_to_execution(self):
        for task in self.assembleQueue.get_task_list()[:]:
            if task.get_status() == 'SUCCESS':
                assemble_log.info(task.get_state() + '*************************')
                if task.get_state().upper() == "ASSEMBLE FINISHED":
                    self.__pipe.send(task)
                    assemble_log.info(
                        '[send_task_to_execution]-Send {} to execution engine'.format(task.get_name()))
                    self.get_signal_after_send(task)
                else:
                    time.sleep(1)
                    continue
            elif task.get_status() != '':
                '''
                deal with build fail
                '''
                error_msg_instance = ErrorMsg(EngineCode().assembly_engine, ErrorLevel().mark_task,
                                              "build task fail,mark state to unknown")
                error_handle_instance = ErrorHandler(error_msg_instance)
                handle_res = error_handle_instance.handle(task=task, state="unknown")
                if not handle_res:
                    continue

        time.sleep(10)

    def get_signal_after_send(self, task):
        send_status = self.__pipe.recv()
        if send_status == task.get_name():
            self.assembleQueue.remove_task(task)
            assemble_log.info(
                '[fresh_queue_execution] {} is removed from assemble queue'.format(task.get_name()))
            assemble_log.info(
                '[fresh_queue_execution]task left in assemble queue: %d' %
                len(self.assembleQueue.get_task_list()))
        else:
            '''
            deal with send task to execute engine fail
            '''
            error_msg_instance = ErrorMsg(EngineCode().assembly_engine, ErrorLevel().record_and_continue,
                                          "send task to execute engine fail")
            error_handle_instance = ErrorHandler(error_msg_instance)
            error_handle_instance.handle()
            assemble_log.info(
                '[fresh_queue_execution]-----send task and received task is not the same one- ----------'
            )

    def get_os_type(self, task):
        build_server_os = ''
        for i in task.get_uut_list():
            if 'wes' in i.get_version().lower():
                build_server_os = 'win'
            elif 'tp' in i.get_version().lower():
                build_server_os = 'linux'
        return build_server_os

    def __refresh_temp_task_list(self, os, temp_task_list):
        while True:
            assemble_log.info('=======================Begin to fresh temp task list==========================')
            for task in self.assembleQueue.get_task_list():
                if task.get_state().upper() == 'WAIT ASSEMBLE' and self.get_os_type(task) == os:
                    temp_task_list.append(task)
            if not temp_task_list:
                assemble_log.info('---No valid task, waiting for new task-----')
                time.sleep(self.loop_interval)
            else:
                return temp_task_list

    def __refresh_temp_node_list(self, temp_node_list, build_node_type):
        while True:
            assemble_log.info('=======================Begin to fresh temp node list==========================')
            # May need to refresh the node status in JIRA, so far so good
            for build_node in self.__build_node_list:
                if build_node.state == 'Idle' and isinstance(build_node, build_node_type):
                    temp_node_list.append(build_node)
            if not temp_node_list:
                assemble_log.info('---No valid build host, waiting for new node-----')
                time.sleep(self.loop_interval)
            else:
                return temp_node_list

    def validate_task(self, task):
        s_validator = ScriptValidator()
        if not s_validator.validate(task):
            error_msg_instance = ErrorMsg(EngineCode().assembly_engine, ErrorLevel().record_and_continue,
                                          "validate task script in  {} fail".format(task.get_name()))
            error_handle_instance = ErrorHandler(error_msg_instance)
            error_handle_instance.handle()
            return False
        h_validator = HostValidator()
        for uut in task.get_uut_list():
            if not h_validator.validate_uut(uut):
                error_msg_instance = ErrorMsg(EngineCode().assembly_engine, ErrorLevel().record_and_continue,
                                              "validate task uut in {} fail on {}".format(task.get_name(),uut))
                error_handle_instance = ErrorHandler(error_msg_instance)
                error_handle_instance.handle()
                return False
        return True

    def build(self, task, node, os):
        try:
            print('start build {} on {}'.format(task.get_name(), node.get_hostname()))
            task.build(node)
            print(20 * '*')
            print(task.get_status(), task.get_exe_file_list())
            print(20 * '*')
            print('build finished {} on {}'.format(task.get_name(), node.get_hostname()))
            task.set_state('Assemble Finished')
            node.state = 'Idle'
            if os == 'win':
                self.current_thread_count_win -= 1
            elif os == 'linux':
                self.current_thread_count_linux -= 1
        except Exception as e:
            assemble_log.error('New thread Error, Exception:\n{}'.format(e))
            task.set_state('WAIT ASSEMBLE')
            node.state = 'Idle'
            if os == 'win':
                self.current_thread_count_win -= 1
            elif os == 'linux':
                self.current_thread_count_linux -= 1

    def create_os_thread(self, os, build_node_type, temp_task_list, temp_node_list, current_thread, max_thread):
        while True:
            print('=======================================================')
            print('==========Begin to Start New Assemble Thread==============')
            print('=======================================================')
            self.create_build_thread(os, build_node_type, temp_task_list, temp_node_list, current_thread,
                                     max_thread)

    def create_build_thread(self, os, build_node_type, temp_task_list, temp_node_list, current_thread, max_thread):
        assemble_log.info('[thread_assembler] task_list left: {}'.format(len(temp_task_list)))
        if not temp_task_list:
            time.sleep(self.loop_interval)
            temp_task_list = self.__refresh_temp_task_list(os, temp_task_list)
        assemble_task = temp_task_list[0]
        temp_task_list.remove(assemble_task)
        if not temp_node_list:
            temp_node_list = self.__refresh_temp_node_list(temp_node_list, build_node_type)
        assemble_node = temp_node_list[0]
        temp_node_list.remove(assemble_node)
        while True:
            try:
                if current_thread >= max_thread:
                    assemble_log.info('Windows Assemble Thread is full, wait for task finish')
                    time.sleep(self.loop_interval)
                else:
                    assemble_task.set_state('ASSEMBLING')
                    assemble_node.state = 'Busy'
                    current_thread += 1
                    new_thread = threading.Thread(target=self.build, args=(assemble_task, assemble_node, os))
                    new_thread.setDaemon(True)
                    new_thread.start()
                    new_thread.join(2)
                    break
            except Exception as e:
                assemble_log.error('New Thread Error, Exception: \n{}'.format(e))
                current_thread -= 1
                assemble_task.set_state('WAIT ASSEMBLE')
                assemble_node.state = 'Idle'

    def __assemble(self):
        while True:
            win_thread = threading.Thread(target=self.create_os_thread, args=(
                'win', WindowsBuildHost, self.temp_task_win, self.temp_node_win, self.current_thread_count_win,
                self.max_thread_count_win))
            win_thread.start()
            linux_thread = threading.Thread(target=self.create_os_thread, args=(
                'linux', LinuxBuildHost, self.temp_task_linux, self.temp_node_linux, self.current_thread_count_linux,
                self.max_thread_count_linux))
            linux_thread.start()
            win_thread.join()
            linux_thread.join()
