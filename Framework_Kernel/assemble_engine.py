# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:27 PM
# @Author  : balance
# @Email   : balance.cheng@hp.com
# @File    : AssembleEngine.py
# @Project : Automation-Framework
from Framework_Kernel.engine import Engine
from Framework_Kernel.task_queue import AssembleQueue
from Framework_Kernel.analyzer import Analyzer
from Common_Library.email_operator import Email
from Framework_Kernel.task import Task
from Framework_Kernel.host import WindowsExecuteHost, LinuxExecuteHost
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
        self.assembleQueue = AssembleQueue()
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
                self.assembleQueue.remove_task(task)
                e = Email()
                e.send_email('send_task_to_execution', task.get_email(),
                             '[send_task_to_execution] !!!ERROR ERROR!!!, {} is removed from assemble queue', 'html')
                e.disconnect()
                assemble_log.error(
                    '[send_task_to_execution] !!!ERROR ERROR!!!, {} is removed from assemble queue'
                    .format(task.get_name()))
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

    def __assemble(self):
        while True:
            assemble_log.info(
                '[thread_assemble_task] ************************ Begine to assemble... **********************'
            )
            h_validator = HostValidator()
            s_validator = ScriptValidator()
            try:
                for task in self.assembleQueue.get_task_list():
                    if task.get_state().upper() == 'WAIT ASSEMBLE':
                        task.set_state('ASSEMBLING')
                        b_host = self.__build_list[0]
                        for uut in task.get_uut_list():
                            h_validator.validate_uut(uut)
                        res = s_validator.validate(task)
                        """
                        check task is ok
                        """
                        if not res:
                            error_msg_instance = ERROR_MSG(ENGINE_CODE().assembly_engine,
                                                            ERROR_LEVEL().drop_task,
                                                            "check task fail,drop it")
                            error_handle_instance = ErrorHandler(error_msg_instance)
                            handle_res = error_handle_instance.handle(task=Task, task_queue=self.assembleQueue)
                            if not handle_res:
                                continue

                        self.assembleQueue.assemble(task, b_host)
                        print(20 * '*')
                        print(task.get_status(), task.get_exe_file_list())
                        print(20 * '*')
                        task.set_state('Assemble Finished')
                        assemble_log.info(
                            '[thread_assemble_task] **************{} assemble finished****************'
                            .format(task.get_name()))
            except Exception as e:
                print(e)
            # print(
            #     '[thread_assemble_task]--------------------------------------------------------------------------------'
            # )
            time.sleep(10)
