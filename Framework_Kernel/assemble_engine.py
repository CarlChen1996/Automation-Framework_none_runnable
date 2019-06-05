# -*- coding: utf-8 -*-
# @Time    : 5/13/2019 1:27 PM
# @Author  : balance
# @Email   : balance.cheng@hp.com
# @File    : AssembleEngine.py
# @Project : Automation-Framework
from Framework_Kernel.engine import Engine
from Framework_Kernel.queue import AssembleQueue
from Framework_Kernel.analyzer import Analyzer
from Framework_Kernel.task import Task
from Framework_Kernel.host import WindowsExecuteHost
from Framework_Kernel.validator import HostValidator
from Framework_Kernel.validator import ScriptValidator
from Framework_Kernel.script import Script
from Framework_Kernel.log import Log
from multiprocessing import Process
import time
import threading
import os

log = Log(name='assemble')
root = os.getcwd()
plan_root = os.path.join(root, 'Configuration\\test_plan')


class AssembleEngine(Engine):
    def __init__(self, pipe, build_list):
        self.pipe = pipe
        self.assembleQueue = AssembleQueue()
        self.tasklist = []
        self.build_list = build_list

    def start(self):
        self.assembler = Process(target=self.start_thread,
                                 name='framework_Assembler',
                                 args=())
        self.assembler.daemon = True
        self.status = self.assembler
        self.assembler.start()

    def stop(self):
        self.assembler.terminate()

    def fresh_queue_testplan(self):
        """
        refresh Queue from test plan in test folder
        :return: None
        """
        while True:
            print('[Thread_fresh_testplan] ***************begin to refresh queue *****************')
            temp_list = os.listdir(plan_root)
            file_list = []
            for i in temp_list:
                if 'PASS' in i.upper() or 'FAIL' in i.upper():
                    time.sleep(3)
                    continue
                file_list.append(os.path.join(plan_root, i))
            analyzer = Analyzer(file_list)
            data = analyzer.load()
            task_data = analyzer.generate(data)
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
            #                           file_path:c:\\xxxx\\xxx\\testplan\\xxx.yml}
            # uutinformation: {         hostname: uut1,
            #                           ip:1.1.1.1,
            #                           mac:1234566,
            #                           version: win7}}
            # ************************************************************************
            """
            for taskitem in task_source_list:
                task = Task(taskitem['name'], taskitem['needbuild'])
                task.set_state('Wait Assemble')
                for script in taskitem['testscripts']:
                    task.insert_script(Script(name=script))
                for uutitem in taskitem['uutlist']:
                    # ------需要根据 uut的os 来实例，目前没实现，只考虑windows------------
                    uut = WindowsExecuteHost(ip=uutitem['ip'],
                                             hostname=uutitem['hostname'],
                                             version=uutitem['version'],
                                             mac=uutitem['mac'])
                    task.insert_uut_list(uut)
                log.log('[thread_1]--insert {} to assemble queue list'.format(
                    task.get_name()))
                self.assembleQueue.insert_task(task=task)
                # -------------------rename task plan name -------------------------
                os.rename(taskitem['file_path'], taskitem['file_path'] + 'PASS')
                print('rename finished', taskitem['file_path'] + 'PASS')
            log.log(
                '[thread_1] ***************finish refresh queue *****************'
            )
            log.log('[thread_1] left task in assemble queue: {}'.format(
                len(self.assembleQueue.get_task_list())))
            time.sleep(3)

    def fresh_queue_execution(self):
        while True:
            print('[fresh_queue_execution]-------begin to refresh----fresh_queue_execution----------------')
            print(self.assembleQueue.get_task_list())
            for task in self.assembleQueue.get_task_list()[:]:
                print(task.get_state(), '*************************')
                if task.get_state().upper() == "ASSEMBLE FINISHED":
                    self.pipe.send(task)
                    log.log('[thread_fresh]-Send {} to execution engine'.format(task.get_name()))
                    send_status = self.pipe.recv()
                    if send_status == task.get_name():
                        self.assembleQueue.remove_task(task)
                        print('[thread fresh] {} is removed from assmebleQueue'.format(task.get_name()))
                        log.log('[thread_2]task left in assemble queue: %d' %
                                len(self.assembleQueue.get_task_list()))
                    else:
                        print('[thread fresh queue via execution]-----send task and received task is not the same one- ----------')
                else:
                    time.sleep(1)
                    continue
            time.sleep(3)

    def assemble(self, build_list):
        while not False:
            assemble_function(self.assembleQueue, build_list)
            time.sleep(1)

    def start_thread(self):
        refreshQ_thread = threading.Thread(target=self.fresh_queue_testplan,
                                           name='thread_1',
                                           args=())
        refreshQ_thread.setDaemon(True)
        refreshQ_thread.start()
        refreshQ_execute = threading.Thread(target=self.fresh_queue_execution)
        refreshQ_execute.setDaemon(True)
        refreshQ_execute.start()
        assembler_thread = threading.Thread(target=self.assemble, name='thread_2', args=(self.build_list, ))
        assembler_thread.setDaemon(True)
        assembler_thread.start()
        assembler_thread.join()


def assemble_function(assembleQueue, build_list):
    log.log(
        '[thread_2] ************************ Begine to assemble... **********************'
    )
    h_validator = HostValidator()
    s_validator = ScriptValidator()
    try:
        for task in assembleQueue.get_task_list():
            if task.get_state().upper() == 'WAIT ASSEMBLE':
                task.set_state('ASSEMBLING')
                b_host = build_list[0]
                for uut in task.get_uut_list():
                    h_validator.validate(uut)
                s_validator.validate(task)
                assembleQueue.build_task(task, b_host)
                task.set_state('Assemble Finished')
                log.log(
                    '[thread_2] **************{} assemble finished****************'.
                    format(task.get_name()))
    except Exception as e:
        print(e)
    print(
        '[thread_2]--------------------------------------------------------------------------------'
    )


if __name__ == '__main__':
    assemble_function()
