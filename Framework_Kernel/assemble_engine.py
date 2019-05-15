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
import time


log = Log(name='assemble')


class AssembleEngine(Engine):
    def __init__(self):
        self.assembleQueue = AssembleQueue()
        self.tasklist = []
    def start(self, build_list):

        while 1:
            execute(self.assembleQueue, build_list, self.tasklist)
            time.sleep(3)
            print('=======================================')
            print('       waitting for new task ...')
            print('=======================================')
            break


def execute(assembleQueue, build_list, task_list):
    # assembleQueue = AssembleQueue()
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
        assembleQueue.insert_task(task=task)
    print('-------------------------------------------')
    h_validator = HostValidator()
    s_validator = ScriptValidator()
    b_host = build_list[0]
    """
    2019/05/15
    assembly one task then back to refresh assemble queue,
    so below should remove loop task list, only assemble tasklist[0], 
    modify after review **********************************************************************
    """
    for task in assembleQueue.get_task_list()[:]:
        for uut in task.get_uut_list():
            h_validator.validate(uut)
        s_validator.validate(task)
        assembleQueue.build_task(task, b_host)
        log.log('insert {} into global task_list'.format(task.get_name()))
        task_list.append(task)
        log.log('remove {} from assemble queue list'.format(task.get_name()))
        assembleQueue.remove_task(task)
        print('task left in assemble queue:', len(assembleQueue.get_task_list()))
        print('------------------------------------')
        # ＝＝＝＝＝＝＝＝＝＝通过判读build server的status随机选择要用的 build server =============
    print('all task assemble finished')


if __name__ == '__main__':
    execute()
