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
from multiprocessing import Pipe
import time
import threading


log = Log(name='assemble')


class AssembleEngine(Engine):
    def __init__(self, pipe, build_list):
        self.pipe = pipe
        self.assembleQueue = AssembleQueue()
        self.tasklist = []
        self.build_list = build_list

    def new_thread(self):
        """
        refresh Queue
        :return:
        """
        while 1:
            print('#[thread1_fresh Assemble Queue] ***************begin to refresh queue *****************')

            analyzor = Analyzer(['.\\Configuration\\testplan.yml'])
            data = analyzor.load()
            task_data = analyzor.generate(data)
            task_source_list = []
            """
            # ***************convert source data to task source list *****************
            # tasklist contains task source
            # tasklist member(taskitem): {
            #                               name:task1,
            #                               testscripts:[script1, script2,],
            #                               uutlist:[{uut1:uutinformation},
            #                               {uut2:uutinformation}],
            #                               needbuild:true}
            # uutinformation: {uut1:{
            #                           hostname: uut1,
            #                           ip:1.1.1.1,
            #                           mac:1234566,
            #                           version: win7}}
            # ************************************************************************
            """
            for task_source in task_data:
                task_source_list = list(task_source.values())
            for taskitem in task_source_list:
                task = Task(taskitem['name'], taskitem['needbuild'])
                for script in taskitem['testscripts']:
                    task.insert_script(Script(name=script))
                """
                # *************convert uut source data to uut source list ************
                #
                """
                uut_source_list = []
                for uut_source in taskitem['uutlist']:
                    uut_source_list.append(list(uut_source.values())[0])
                for uutitem in uut_source_list:
                    # ------需要根据 uut的os 来实例，目前没实现，只考虑windows------------
                    uut = WindowsExecuteHost(ip=uutitem['ip'],
                                             hostname=uutitem['hostname'],
                                             version=uutitem['version'],
                                             mac=uutitem['mac'])
                    task.insert_uut_list(uut)
                log.log('inset {} to assembly queue list'.format(task.get_name()))
                print('[thread1_fresh Assemble Queue]---------------insert {} into assembly queue-------'.format(task.get_name()))
                self.assembleQueue.insert_task(task=task)
                print(len(self.assembleQueue.get_task_list()))

            time.sleep(10)

    def new_process(self):
        assembler = Process(target=self.test, name='framework_Assembler', args=(self.pipe, self.build_list))
        assembler.start()
        # self.status = assembler

    def test(self, pipe, build_list):
        refreshQ_thread = threading.Thread(target=self.new_thread, name= 'frame_assembler_new_thread', args=())
        refreshQ_thread.start()
        while not False:
            execute(self.assembleQueue, build_list, pipe)
            # print('=======================================')
            # print('       waitting for new task to assemble...')
            # print('=======================================')
            # break
            time.sleep(1)


def execute(assembleQueue, build_list, pipe):
    print('[thread2_assembly_progress]-------------------------------------------')
    h_validator = HostValidator()
    s_validator = ScriptValidator()
    b_host = build_list[0]
    """
    2019/05/15
    assembly one task then back to refresh assemble queue,
    so below should remove loop task list, only assemble tasklist[0],
    modify after review **********************************************************************
    """
    try:
        if len(assembleQueue.get_task_list()) == 0:
            print('[thread2_assembly_progress]************************ no task in list **********************')
            print('[thread2_assembly_progress]************************ wait for new task to assemble**********************')
            return
        task = assembleQueue.get_task_list()[0]
        for uut in task.get_uut_list():
            h_validator.validate(uut)
        s_validator.validate(task)
        assembleQueue.build_task(task, b_host)
        log.log('insert {} into global task_list'.format(task.get_name()))
        print('[thread2_assembly_progress]---------Send task in assembly {}--------------'.format(task.get_name()))
        pipe.send(task)
        log.log('remove {} from assemble queue list'.format(task.get_name()))
        assembleQueue.remove_task(task)
        print('[thread2_assembly_progress]task left in assemble queue:', len(assembleQueue.get_task_list()))
        print('[thread2_assembly_progress]------------------------------------')
    except Exception as e:
        print(e)
        # ＝＝＝＝＝＝＝＝＝＝通过判读build server的status随机选择要用的 build server =============
    print('[thread2]{} assemble finished'.format(task.get_name()))


if __name__ == '__main__':
    execute()
