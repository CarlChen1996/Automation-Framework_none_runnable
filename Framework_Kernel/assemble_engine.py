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
        self.assembler = Process(target=self.new_thread, name='framework_Assembler', args=())
        self.pipe = pipe
        self.assembleQueue = AssembleQueue()
        self.tasklist = []
        self.build_list = build_list
        self.status = self.assembler

    def freash_queue(self):
        """
        refresh Queue
        :return:
        """
        while 1:
            log.log('[thread_1] ***************begin to refresh queue *****************')
            templist = os.listdir(plan_root)
            filelist = []
            for i in templist:
                if 'PASS' in i.upper() or 'FAIL' in i.upper():
                    time.sleep(3)
                    continue
                filelist.append(os.path.join(plan_root, i))
            analyzor = Analyzer(filelist)
            data = analyzor.load()
            task_data = analyzor.generate(data)
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
                for script in taskitem['testscripts']:
                    task.insert_script(Script(name=script))
                for uutitem in taskitem['uutlist']:
                    # ------需要根据 uut的os 来实例，目前没实现，只考虑windows------------
                    uut = WindowsExecuteHost(ip=uutitem['ip'],
                                             hostname=uutitem['hostname'],
                                             version=uutitem['version'],
                                             mac=uutitem['mac'])
                    task.insert_uut_list(uut)
                log.log('[thread_1]--insert {} to assemble queue list'.format(task.get_name()))
                self.assembleQueue.insert_task(task=task)
                # -------------------rename task plan name -------------------------
                os.rename(taskitem['file_path'], taskitem['file_path']+'PASS')
            log.log('[thread_1] ***************finish refresh queue *****************')
            log.log('[thread_1] left task in assemble queue: {}'.format(len(self.assembleQueue.get_task_list())))
            time.sleep(10)

    def process(self, pipe, build_list):
        while not False:
            assemble(self.assembleQueue, build_list, pipe)
            time.sleep(1)

    def new_thread(self):
        refreshQ_thread = threading.Thread(target=self.freash_queue, name='thread_1', args=())
        refreshQ_thread.setDaemon(True)
        refreshQ_thread.start()
        process_thread = threading.Thread(target=self.process, name='thread_2', args=(self.pipe, self.build_list))
        process_thread.setDaemon(True)
        process_thread.start()
        process_thread.join()

    def start(self):
        self.assembler.start()

    def stop(self):
        self.assembler.terminate()


def assemble(assembleQueue, build_list, pipe):
    log.log('[thread_2] ************************ Begine to assemble... **********************')
    try:
        if len(assembleQueue.get_task_list()) == 0:
            log.log('[thread_2]************************ wait for new task to assemble **********************')
            time.sleep(10)
            return
        h_validator = HostValidator()
        s_validator = ScriptValidator()
        b_host = build_list[0]
        task = assembleQueue.get_task_list()[0]
        for uut in task.get_uut_list():
            h_validator.validate(uut)
        s_validator.validate(task)
        assembleQueue.build_task(task, b_host)
        pipe.send(task)
        log.log('[thread_2]-Send {} to Thread3 (execution engine)'.format(task.get_name()))
        assembleQueue.remove_task(task)
        log.log('[thread_2]-remove {} from assemble queue list'.format(task.get_name()))
        log.log('[thread_2]task left in assemble queue: %d' % len(assembleQueue.get_task_list()))
        log.log('[thread_2] **************{} assemble finished****************'.format(task.get_name()))
    except Exception as e:
        print(e)
    print('[thread_2]--------------------------------------------------------------------------------')


if __name__ == '__main__':
    assemble()
