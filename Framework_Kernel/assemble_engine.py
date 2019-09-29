# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:27 PM
# @Author  : balance
# @Email   : balance.cheng@hp.com
# @File    : AssembleEngine.py
# @Project : Automation-Framework
from Framework_Kernel.engine import Engine
from Framework_Kernel.task_queue import Queue
from Framework_Kernel.analyzer import Analyzer
from Common_Library.email_operator import Email
from Framework_Kernel.task import Task
from Framework_Kernel.host import WindowsExecuteHost, LinuxExecuteHost, WindowsBuildHost, LinuxBuildHost
from Framework_Kernel.validator import HostValidator
from Framework_Kernel.validator import ScriptValidator
from Framework_Kernel.script import Script
from Framework_Kernel.log import assemble_log
from Framework_Kernel.error_handler import ERROR_MSG, ERROR_LEVEL, ErrorHandler, ENGINE_CODE
from multiprocessing import Process
import time
import threading
import os
import datetime


class AssembleEngine(Engine):
    def __init__(self, pipe, build_list):
        self.__pipe = pipe
        self.assembleQueue = Queue()
        self.tasklist = []
        self.__build_list = build_list
        self.test_plan_folder = os.path.join(os.getcwd(), 'Test_Plan')

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
        refreshQ_thread = threading.Thread(target=self.__fresh_queue_testplan,
                                           name='fresh_queue_testplan',
                                           args=())
        refreshQ_thread.setDaemon(True)
        refreshQ_thread.start()
        refreshQ_execute = threading.Thread(
            target=self.__fresh_queue_execution)
        refreshQ_execute.setDaemon(True)
        refreshQ_execute.start()
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
        #                           needbuild:true
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
                '[Thread_fresh_testplan]--insert {} to assemble queue list'.
                    format(task.get_name()))

            if self.validate_task(task):
                self.assembleQueue.insert_task(task=task)

            # -------------------rename task plan name -------------------------
            os.rename(
                taskitem['file_path'], taskitem['file_path']
                                       [:taskitem['file_path'].index('TEST_PLAN')] + 'Loaded_' + taskitem['file_path']
                                       [taskitem['file_path'].index('TEST_PLAN'):])
            assemble_log.info('rename finished' + taskitem['file_path']
            [:taskitem['file_path'].index('TEST_PLAN')] + 'Loaded_' + taskitem['file_path']
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
                        '[send_task_to_execution]-Send {} to execution engine'.
                            format(task.get_name()))
                    self.get_signal_after_send(task)
                else:
                    time.sleep(1)
                    continue
            elif task.get_status() != '':
                '''
                deal with build fail
                '''
                error_msg_instance = ERROR_MSG(ENGINE_CODE().assembly_engine,
                                               ERROR_LEVEL().drop_task,
                                               "build task fail,drop it")
                error_handle_instance = ErrorHandler(error_msg_instance)
                handle_res = error_handle_instance.handle(task=task, task_queue=self.assembleQueue)
                if not handle_res:
                    continue

        time.sleep(10)

    def get_signal_after_send(self, task):
        send_status = self.__pipe.recv()
        if send_status == task.get_name():
            self.assembleQueue.remove_task(task)
            assemble_log.info(
                '[fresh_queue_execution] {} is removed from assemble queue'.
                    format(task.get_name()))
            assemble_log.info(
                '[fresh_queue_execution]task left in assemble queue: %d' %
                len(self.assembleQueue.get_task_list()))
        else:
            assemble_log.info(
                '[fresh_queue_execution]-----send task and received task is not the same one- ----------'
            )

    def get_os_type(self, task):
        build_server_os = ''
        for i in task.get_uut_list():
            if 'wes' in i._Host__version.lower():
                build_server_os = 'win'
            elif 'tp' in i._Host__version.lower():
                build_server_os = 'linux'
        return build_server_os

    def refresh_node_state(self, os):
        pass

    def create_temp_task(self, os):
        temp_task = []
        for task in self.assembleQueue.get_task_list():
            if task.get_state().upper() == 'WAIT ASSEMBLE':
                if self.get_os_type(task) == os:
                    temp_task.append(task)
        return temp_task

    def create_temp_node(self, os):
        temp_node = []
        self.refresh_node_state(os)
        for build_node in self.__build_list:
            if build_node.state == 'Idle':
                if os == 'win':
                    if isinstance(build_node, WindowsBuildHost):
                        temp_node.append(build_node)
                elif os == 'linux':
                    if isinstance(build_node, LinuxBuildHost):
                        temp_node.append(build_node)

        return temp_node

    def validate_task(self, task):
        s_validator = ScriptValidator()
        if not s_validator.validate(task):
            error_msg_instance = ERROR_MSG(ENGINE_CODE().assembly_engine, ERROR_LEVEL().continue_task,
                                           "validate task {} fail".format(task.get_name()))
            error_handle_instance = ErrorHandler(error_msg_instance)
            error_handle_instance.handle()
            return False
        h_validator = HostValidator()
        for uut in task.get_uut_list():
            if not h_validator.validate_uut(uut):
                error_msg_instance = ERROR_MSG(ENGINE_CODE().assembly_engine, ERROR_LEVEL().continue_task,
                                               "validate task uut {} fail".format(task.get_name()))
                error_handle_instance = ErrorHandler(error_msg_instance)
                error_handle_instance.handle()
                return False
        return True


    def build(self, task, node, os):
        try:
            print('start build {} on {}'.format(task.get_name(), node.get_hostname()))
            # for i in range(15):
            #     print('building {} on {}'.format(task.get_name(), node.get_hostname()))
            #     time.sleep(1)
            task.build(node)
            print(20 * '*')
            print(task.get_status(), task.get_exe_file_list())
            print(20 * '*')
            print('build finished {} on {}'.format(task.get_name(), node.get_hostname()))
            task.set_state('Assemble Finished')
            node.state = 'Idle'
            if os == 'win':
                self.count_task_win -= 1
            elif os == 'linux':
                self.count_task_linux -= 1
        except:
            task.set_state('WAIT ASSEMBLE')
            node.state = 'Idle'
            if os == 'win':
                self.count_task_win -= 1
            elif os == 'linux':
                self.count_task_linux -= 1

    def create_task_thread(self, os):
        if os == 'win':
            if self.temp_task_win:
                for task in self.temp_task_win[:]:
                    if self.count_task_win < self.max_count:
                        if self.temp_node_win:
                            node0 = self.temp_node_win[0]
                            self.temp_task_win.remove(task)
                            self.temp_node_win.remove(node0)
                            try:
                                t = threading.Thread(target=self.build, args=(task, node0, 'win'))
                                time.sleep(1)
                                node0.state = 'Busy'
                                self.count_task_win += 1
                                task.set_state('ASSEMBLING')
                                t.start()
                            except Exception as e:
                                print('exception in win assemble {}'.format(str(e)))
                                node0.state = 'Idle'
                                self.count_task_win -= 1
                                task.set_state('WAIT ASSEMBLE')
                        else:
                            self.temp_node_win = self.create_temp_node('win')
                    else:
                        print('win full running')
                        time.sleep(self.loop_interval)
            else:
                time.sleep(self.loop_interval)
                self.temp_task_win = self.create_temp_task('win')
        elif os == 'linux':
            if self.temp_task_linux:
                for task in self.temp_task_linux[:]:
                    if self.count_task_linux < self.max_count:
                        if self.temp_node_linux:
                            node0 = self.temp_node_linux[0]
                            self.temp_task_linux.remove(task)
                            self.temp_node_linux.remove(node0)
                            try:
                                t = threading.Thread(target=self.build, args=(task, node0, 'linux'))
                                time.sleep(1)
                                node0.state = 'Busy'
                                self.count_task_linux += 1
                                task.set_state('ASSEMBLING')
                                t.start()
                            except Exception as e:
                                print('exception in linux assemble {}'.format(str(e)))
                                node0.state = 'Idle'
                                self.count_task_linux -= 1
                                task.set_state('WAIT ASSEMBLE')
                        else:
                            self.temp_node_linux = self.create_temp_node('linux')
                    else:
                        print('linux full running')
                        time.sleep(self.loop_interval)
            else:
                time.sleep(self.loop_interval)
                self.temp_task_linux = self.create_temp_task('linux')
        else:
            return False

    def thread_f(self, os):
        while True:
            self.create_task_thread(os)

    def __assemble(self):
        config_file = os.path.join(os.getcwd(), r'.\Configuration\config_framework_list.yml')
        analyze_hanlder = Analyzer()
        global_settings = analyze_hanlder.analyze_file(config_file)['global_settings']
        self.loop_interval = int(global_settings['LOOP_INTERVAL'])

        self.count_task_win = 0
        self.count_task_linux = 0
        self.max_count = 2
        self.temp_task_win = self.create_temp_task('win')
        self.temp_node_win = self.create_temp_node('win')
        self.temp_task_linux = self.create_temp_task('linux')
        self.temp_node_linux = self.create_temp_node('linux')
        win_thread = threading.Thread(target=self.thread_f, args=('win',))
        win_thread.start()
        linux_thread = threading.Thread(target=self.thread_f, args=('linux',))
        linux_thread.start()
        win_thread.join()
        linux_thread.join()

        # h_validator = HostValidator()
        # s_validator = ScriptValidator()
        # try:
        #     for task in self.assembleQueue.get_task_list():
        #         if task.get_state().upper() == 'WAIT ASSEMBLE':
        #             task.set_state('ASSEMBLING')
        #             b_host = self.__build_list[0]
        #             for uut in task.get_uut_list():
        #                 h_validator.validate_uut(uut)
        #             assemble_log.info(
        #                 'assemble_engine build {} on {}'.format(task.get_name(), b_host.get_hostname()))
        #             print("**************************************************")
        #             print("**************************************************")
        #             print("**************************************************")
        #             print("**************************************************")
        #             print("**************************************************")
        #             task.build(b_host)
        #             print(20 * '*')
        #             print(task.get_status(), task.get_exe_file_list())
        #             print(20 * '*')
        #             task.set_state('Assemble Finished')
        #             assemble_log.info(
        #                 '[thread_assemble_task] **************{} assemble finished****************'
        #                     .format(task.get_name()))
        # except Exception as e:
        #     print(e)
        # # print(
        # #     '[thread_assemble_task]--------------------------------------------------------------------------------'
        # # )
        # time.sleep(10)
